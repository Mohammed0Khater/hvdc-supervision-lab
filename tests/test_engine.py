import json
from pathlib import Path

from hvdc_lab.engine import PlantSimulator
from hvdc_lab.scenarios import load_settings, run_scenario

def test_station_b_unavailable_scenario_is_rejected(tmp_path: Path) -> None:
    summary = run_scenario(
        "station_b_unavailable",
        tmp_path,
        ROOT / "config" / "settings.json",
    )
    event_report = json.loads(Path(summary["events_path"]).read_text(encoding="utf-8"))
    rejected = [
        event
        for event in event_report["events"]
        if event["event_type"] == "COMMAND_REJECTED"
    ]
    assert summary["final_state"] == "STANDBY"
    assert any("Station B is not ready" in item["message"] for item in rejected)

ROOT = Path(__file__).resolve().parents[1]


def make_simulator() -> PlantSimulator:
    return PlantSimulator(load_settings(ROOT / "config" / "settings.json"))


def test_start_and_ramp_to_setpoint() -> None:
    sim = make_simulator()
    assert sim.start().accepted
    assert sim.set_setpoint(900.0).accepted
    first = sim.tick(1.0)
    second = sim.tick(1.0)
    assert first["state"] == "RUNNING"
    assert second["active_power_mw"] == 500.0
    assert second["dc_current_ka"] > 0.0


def test_start_is_rejected_when_communication_is_unhealthy() -> None:
    sim = make_simulator()
    sim.inject(communication_healthy=False)
    result = sim.start()
    assert not result.accepted
    assert "communication" in result.message
    assert sim.state == "STANDBY"


def test_overvoltage_trip_is_delayed_and_latched() -> None:
    sim = make_simulator()
    assert sim.start().accepted
    sim.inject(dc_voltage_kv=455.0)
    first = sim.tick(0.5)
    assert not first["trip_latched"]
    second = sim.tick(0.5)
    assert second["trip_latched"]
    assert second["trip_cause"] == "DC_OVERVOLTAGE"
    assert second["state"] == "TRIPPED"
    assert sim.reset_trip().accepted is False


def test_trip_reset_is_accepted_after_fault_clears() -> None:
    sim = make_simulator()
    assert sim.start().accepted
    sim.inject(dc_current_ka=3.5)
    sim.tick(1.0)
    assert sim.trip_latched
    sim.clear_injections()
    assert sim.reset_trip().accepted
    assert sim.state == "STANDBY"


def test_bad_quality_causes_alarm_and_trip() -> None:
    sim = make_simulator()
    assert sim.start().accepted
    sim.inject(sensor_quality_good=False)
    snapshot = sim.tick(1.0)
    assert "MEASUREMENT_QUALITY_BAD" in snapshot["active_alarms"]
    assert snapshot["trip_cause"] == "BAD_MEASUREMENT_QUALITY"


def test_cooling_warning_does_not_trip_below_trip_threshold() -> None:
    sim = make_simulator()
    sim.inject(cooling_temperature_c=85.0)
    snapshot = sim.tick(1.0)
    assert "COOLING_TEMPERATURE_HIGH_ALARM" in snapshot["active_alarms"]
    assert not snapshot["trip_latched"]


def test_scenario_runner_writes_csv_and_event_json(tmp_path: Path) -> None:
    summary = run_scenario("dc_overvoltage", tmp_path, ROOT / "config" / "settings.json")
    assert summary["trip_latched"] is True
    assert summary["trip_cause"] == "DC_OVERVOLTAGE"
    assert Path(summary["csv_path"]).exists()
    assert Path(summary["events_path"]).exists()


def test_setpoint_outside_training_range_is_rejected() -> None:
    sim = make_simulator()
    result = sim.set_setpoint(1200.0)
    assert not result.accepted
    assert sim.requested_power_mw == 900.0


def test_injection_clear_restores_original_measurement() -> None:
    sim = make_simulator()
    sim.inject(dc_voltage_kv=455.0, communication_healthy=False)
    sim.clear_injections()
    assert sim.telemetry["dc_voltage_kv"] == 400.0
    assert sim.telemetry["communication_healthy"] is True


def test_start_is_rejected_when_station_is_not_ready() -> None:
    sim = make_simulator()
    sim.inject(station_b_ready=False)
    result = sim.start()
    assert not result.accepted
    assert "Station B is not ready" in result.message


def test_stop_returns_running_link_to_standby() -> None:
    sim = make_simulator()
    assert sim.start().accepted
    sim.tick(1.0)
    result = sim.stop()
    assert result.accepted
    assert sim.state == "STANDBY"
    assert sim.telemetry["active_power_mw"] == 0.0


def test_stale_telemetry_trip_is_delayed_and_latched() -> None:
    sim = make_simulator()
    assert sim.start().accepted
    sim.inject(telemetry_age_s=5.0)
    first = sim.tick(1.0)
    assert not first["trip_latched"]
    assert "TELEMETRY_STALE" in first["active_alarms"]
    second = sim.tick(1.0)
    assert second["trip_latched"]
    assert second["trip_cause"] == "STALE_TELEMETRY"
