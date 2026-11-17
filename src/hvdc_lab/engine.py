"""A deterministic, training-only two-terminal HVDC supervisory simulator.

This is deliberately NOT a converter model, protection relay, or safety system.
All values and thresholds are synthetic and exist only for software exercises.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class CommandResult:
    accepted: bool
    message: str


class PlantSimulator:
    """Small deterministic model used by scenario tests and the OPC UA gateway."""

    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        settings = settings or {}
        self.settings = settings
        model = settings.get("model", {})
        self.limits = settings.get("limits", {})
        self.timing = settings.get("timing", {})
        self.time_s = 0.0
        self.state = "STANDBY"
        self.requested_power_mw = float(model.get("default_power_setpoint_mw", 900.0))
        self.ramp_rate_mw_per_s = float(model.get("ramp_rate_mw_per_s", 250.0))
        self.trip_latched = False
        self.trip_cause = ""
        self.active_alarms: list[str] = []
        self.events: list[dict[str, Any]] = []
        self._trip_timers: dict[str, float] = {}
        self._overrides: dict[str, Any] = {}
        self._pre_injection_values: dict[str, Any] = {}
        self.telemetry: dict[str, Any] = {
            "dc_voltage_kv": float(model.get("nominal_dc_voltage_kv", 400.0)),
            "dc_current_ka": 0.0,
            "active_power_mw": 0.0,
            "cooling_temperature_c": 45.0,
            "communication_healthy": True,
            "sensor_quality_good": True,
            "telemetry_age_s": 0.0,
            "station_a_ready": True,
            "station_b_ready": True,
        }
        self._record("INITIALIZED", "Simulator initialized in STANDBY")

    def _record(self, event_type: str, message: str) -> None:
        self.events.append({
            "time_s": round(self.time_s, 3),
            "event_type": event_type,
            "message": message,
        })

    def set_setpoint(self, power_mw: float) -> CommandResult:
        minimum = float(self.limits.get("minimum_power_mw", 0.0))
        maximum = float(self.limits.get("maximum_power_mw", 1000.0))
        if not minimum <= power_mw <= maximum:
            msg = (
                f"Rejected setpoint {power_mw:.1f} MW; allowed training range is "
                f"{minimum:.1f}-{maximum:.1f} MW"
            )
            self._record("COMMAND_REJECTED", msg)
            return CommandResult(False, msg)
        self.requested_power_mw = float(power_mw)
        msg = f"Accepted requested power setpoint {power_mw:.1f} MW"
        self._record("SETPOINT_ACCEPTED", msg)
        return CommandResult(True, msg)

    def start(self) -> CommandResult:
        if self.trip_latched:
            return self._reject("Start rejected: a trip is latched; investigate and reset first")
        checks = [
            (self.telemetry["communication_healthy"], "communication link is unhealthy"),
            (self.telemetry["sensor_quality_good"], "measurement quality is BAD"),
            (
                self.telemetry["telemetry_age_s"]
                <= float(self.limits.get("stale_data_limit_s", 2.0)),
                "telemetry is stale",
            ),
            (self.telemetry["station_a_ready"], "Station A is not ready"),
            (self.telemetry["station_b_ready"], "Station B is not ready"),
        ]
        for passed, reason in checks:
            if not passed:
                return self._reject(f"Start rejected: {reason}")
        if self.state == "RUNNING":
            return self._reject("Start rejected: link is already RUNNING")
        self.state = "RUNNING"
        msg = "Start accepted; simulated link entered RUNNING state"
        self._record("START_ACCEPTED", msg)
        return CommandResult(True, msg)

    def stop(self) -> CommandResult:
        if self.trip_latched:
            return self._reject(
                "Normal stop not applied: trip is latched; "
                "the simulated link is already in a trip state"
            )
        self.state = "STANDBY"
        self.telemetry["active_power_mw"] = 0.0
        self.telemetry["dc_current_ka"] = 0.0
        msg = "Stop accepted; simulated link returned to STANDBY"
        self._record("STOP_ACCEPTED", msg)
        return CommandResult(True, msg)

    def reset_trip(self) -> CommandResult:
        if not self.trip_latched:
            return self._reject("Reset rejected: no trip is currently latched")
        active_trip = self._active_trip_conditions()
        if active_trip:
            message = "Reset rejected: fault condition remains active: " + ", ".join(active_trip)
            return self._reject(message)
        self.trip_latched = False
        self.trip_cause = ""
        self._trip_timers.clear()
        self.state = "STANDBY"
        msg = "Trip reset accepted; simulated link returned to STANDBY"
        self._record("TRIP_RESET", msg)
        return CommandResult(True, msg)

    def _reject(self, message: str) -> CommandResult:
        self._record("COMMAND_REJECTED", message)
        return CommandResult(False, message)

    def inject(self, **values: Any) -> None:
        """Apply persistent synthetic scenario overrides to telemetry fields."""
        allowed = set(self.telemetry)
        unknown = set(values) - allowed
        if unknown:
            raise ValueError(f"Unsupported telemetry override(s): {', '.join(sorted(unknown))}")
        for key, value in values.items():
            if key not in self._pre_injection_values:
                self._pre_injection_values[key] = self.telemetry[key]
            self._overrides[key] = value
            self.telemetry[key] = value
        injected = ", ".join(f"{key}={value}" for key, value in values.items())
        self._record("SCENARIO_INJECTION", "Injected: " + injected)

    def clear_injections(self) -> None:
        """Restore every overridden signal to the value it had before injection."""
        for key, original_value in self._pre_injection_values.items():
            self.telemetry[key] = original_value
        self._overrides.clear()
        self._pre_injection_values.clear()
        self._record("SCENARIO_INJECTION_CLEARED", "Cleared all synthetic telemetry overrides")

    def _active_trip_conditions(self) -> list[str]:
        t = self.telemetry
        limits = self.limits
        conditions: list[str] = []
        if t["dc_voltage_kv"] >= float(limits.get("dc_overvoltage_trip_kv", 450.0)):
            conditions.append("DC_OVERVOLTAGE")
        if t["dc_voltage_kv"] <= float(limits.get("dc_undervoltage_trip_kv", 350.0)):
            conditions.append("DC_UNDERVOLTAGE")
        if t["dc_current_ka"] >= float(limits.get("dc_overcurrent_trip_ka", 3.2)):
            conditions.append("DC_OVERCURRENT")
        supervisory_active = self.state in {"RUNNING", "TRIPPED"}
        if not t["communication_healthy"] and supervisory_active:
            conditions.append("COMMUNICATION_LOSS")
        if not t["sensor_quality_good"] and supervisory_active:
            conditions.append("BAD_MEASUREMENT_QUALITY")
        if t["cooling_temperature_c"] >= float(limits.get("cooling_trip_c", 95.0)):
            conditions.append("COOLING_OVERTEMPERATURE")
        if (
            t["telemetry_age_s"] > float(limits.get("stale_data_limit_s", 2.0)) 
            and supervisory_active
        ): 
            conditions.append("STALE_TELEMETRY")
        return conditions

    def _evaluate_protection(self, dt_s: float) -> None:
        t = self.telemetry
        limits = self.limits
        alarms: list[str] = []

        if t["dc_voltage_kv"] > float(limits.get("dc_overvoltage_alarm_kv", 430.0)):
            alarms.append("DC_VOLTAGE_HIGH_ALARM")
        if t["dc_voltage_kv"] < float(limits.get("dc_undervoltage_alarm_kv", 370.0)):
            alarms.append("DC_VOLTAGE_LOW_ALARM")
        if t["dc_current_ka"] > float(limits.get("dc_overcurrent_alarm_ka", 2.8)):
            alarms.append("DC_CURRENT_HIGH_ALARM")
        if t["cooling_temperature_c"] > float(limits.get("cooling_alarm_c", 80.0)):
            alarms.append("COOLING_TEMPERATURE_HIGH_ALARM")
        if not t["communication_healthy"]:
            alarms.append("COMMUNICATION_UNHEALTHY")
        if not t["sensor_quality_good"]:
            alarms.append("MEASUREMENT_QUALITY_BAD")
        if t["telemetry_age_s"] > float(limits.get("stale_data_limit_s", 2.0)):
            alarms.append("TELEMETRY_STALE")

        self.active_alarms = alarms
        trip_conditions = self._active_trip_conditions()
        delay_by_code = {
            "DC_OVERVOLTAGE": float(self.timing.get("voltage_trip_delay_s", 1.0)),
            "DC_UNDERVOLTAGE": float(self.timing.get("voltage_trip_delay_s", 1.0)),
            "DC_OVERCURRENT": float(self.timing.get("current_trip_delay_s", 1.0)),
            "COMMUNICATION_LOSS": float(self.timing.get("communication_trip_delay_s", 2.0)),
            "BAD_MEASUREMENT_QUALITY": float(self.timing.get("bad_quality_trip_delay_s", 1.0)),
            "COOLING_OVERTEMPERATURE": float(self.timing.get("cooling_trip_delay_s", 2.0)),
            "STALE_TELEMETRY": float(self.timing.get("stale_data_trip_delay_s", 2.0)),
        }
        for code in list(self._trip_timers):
            if code not in trip_conditions:
                self._trip_timers[code] = 0.0
        for code in trip_conditions:
            self._trip_timers[code] = self._trip_timers.get(code, 0.0) + dt_s
            if not self.trip_latched and self._trip_timers[code] >= delay_by_code[code]:
                self.trip_latched = True
                self.trip_cause = code
                self.state = "TRIPPED"
                self._record("PROTECTIVE_TRIP", f"Training trip latched: {code}")
                break

    def tick(self, dt_s: float = 1.0) -> dict[str, Any]:
        if dt_s <= 0:
            raise ValueError("dt_s must be greater than zero")
        self.time_s = round(self.time_s + dt_s, 6)

        if self.state == "RUNNING" and not self.trip_latched:
            power = float(self.telemetry["active_power_mw"])
            power = min(self.requested_power_mw, power + self.ramp_rate_mw_per_s * dt_s)
            self.telemetry["active_power_mw"] = power
            voltage = max(float(self.telemetry["dc_voltage_kv"]), 1.0)
            self.telemetry["dc_current_ka"] = power / voltage
        else:
            self.telemetry["active_power_mw"] = 0.0
            self.telemetry["dc_current_ka"] = 0.0

        for key, value in self._overrides.items():
            self.telemetry[key] = value

        self._evaluate_protection(dt_s)
        if self.trip_latched:
            self.state = "TRIPPED"
            # In this training model, a trip forces the simulated power/current to zero.
            self.telemetry["active_power_mw"] = 0.0
            self.telemetry["dc_current_ka"] = 0.0

        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        return {
            "time_s": round(self.time_s, 3),
            "timestamp_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "state": self.state,
            "requested_power_mw": round(self.requested_power_mw, 3),
            "dc_voltage_kv": round(float(self.telemetry["dc_voltage_kv"]), 3),
            "dc_current_ka": round(float(self.telemetry["dc_current_ka"]), 4),
            "active_power_mw": round(float(self.telemetry["active_power_mw"]), 3),
            "cooling_temperature_c": round(float(self.telemetry["cooling_temperature_c"]), 3),
            "communication_healthy": bool(self.telemetry["communication_healthy"]),
            "sensor_quality_good": bool(self.telemetry["sensor_quality_good"]),
            "telemetry_age_s": round(float(self.telemetry["telemetry_age_s"]), 3),
            "station_a_ready": bool(self.telemetry["station_a_ready"]),
            "station_b_ready": bool(self.telemetry["station_b_ready"]),
            "trip_latched": self.trip_latched,
            "trip_cause": self.trip_cause,
            "active_alarms": list(self.active_alarms),
        }
