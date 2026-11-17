"""Scenario loading and deterministic scenario execution."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .engine import PlantSimulator

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "settings.json"
SCENARIO_DIR = ROOT / "config" / "scenarios"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_settings(path: Path | None = None) -> dict[str, Any]:
    return load_json(path or DEFAULT_CONFIG)


def list_scenarios() -> list[str]:
    return sorted(path.stem for path in SCENARIO_DIR.glob("*.json"))


def run_scenario(name: str, output_dir: Path, settings_path: Path | None = None) -> dict[str, Any]:
    if name not in list_scenarios():
        raise ValueError(f"Unknown scenario '{name}'. Available: {', '.join(list_scenarios())}")
    settings = load_settings(settings_path)
    scenario = load_json(SCENARIO_DIR / f"{name}.json")
    simulator = PlantSimulator(settings)
    dt = float(scenario.get("step_s", 1.0))
    duration = float(scenario.get("duration_s", 20.0))
    events = sorted(scenario.get("events", []), key=lambda item: float(item.get("at_s", 0.0)))
    next_event = 0
    rows: list[dict[str, Any]] = []
    steps = int(duration / dt)

    for step_index in range(steps + 1):
        current_time = round(step_index * dt, 6)
        while (
            next_event < len(events)
            and float(events[next_event].get("at_s", 0.0)) <= current_time
        ):
            event = events[next_event]
            event_type = event.get("type")
            if event_type == "command":
                command = event.get("command")
                if command == "start":
                    simulator.start()
                elif command == "stop":
                    simulator.stop()
                elif command == "reset_trip":
                    simulator.reset_trip()
                else:
                    raise ValueError(f"Unsupported scenario command: {command}")
            elif event_type == "setpoint":
                simulator.set_setpoint(float(event["power_mw"]))
            elif event_type == "inject":
                simulator.inject(**event.get("values", {}))
            else:
                raise ValueError(f"Unsupported scenario event type: {event_type}")
            next_event += 1
        if step_index == 0:
            rows.append(simulator.snapshot())
        else:
            rows.append(simulator.tick(dt))

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{name}_telemetry.csv"
    json_path = output_dir / f"{name}_events.json"
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            flattened = dict(row)
            flattened["active_alarms"] = ";".join(row["active_alarms"])
            writer.writerow(flattened)
    with json_path.open("w", encoding="utf-8") as handle:
        report = {
            "scenario": scenario,
            "events": simulator.events,
            "final_snapshot": rows[-1],
        }
        json.dump(report, handle, indent=2)

    return {
        "scenario": name,
        "description": scenario.get("description", ""),
        "samples": len(rows),
        "final_state": rows[-1]["state"],
        "trip_latched": rows[-1]["trip_latched"],
        "trip_cause": rows[-1]["trip_cause"],
        "active_alarms": rows[-1]["active_alarms"],
        "csv_path": str(csv_path),
        "events_path": str(json_path),
    }
