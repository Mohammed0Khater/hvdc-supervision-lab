# Scenario Catalog

All scenarios use invented values and simplified behavior. The values are selected for testability, not from a real plant or standard.

| File | Event | Expected result |
|---|---|---|
| `normal.json` | Start; set 900 MW | Remains RUNNING without trip |
| `dc_overvoltage.json` | Inject 455 kV | High-voltage alarm and `DC_OVERVOLTAGE` latched trip |
| `dc_overcurrent.json` | Inject 3.5 kA | Current alarm and `DC_OVERCURRENT` latched trip |
| `communication_loss.json` | Communication flag false | Communication alarm and delayed `COMMUNICATION_LOSS` trip |
| `cooling_alarm.json` | Inject 85 °C | Cooling warning without trip |
| `bad_measurement_quality.json` | Quality flag false | Quality alarm and `BAD_MEASUREMENT_QUALITY` trip |
| `startup_interlock.json` | Communication unhealthy before start | Start command rejected; state remains STANDBY |
| `stale_telemetry.json` | Inject telemetry age of 5 seconds while RUNNING | Stale-data alarm and delayed `STALE_TELEMETRY` trip |

To run the full set:

```powershell
hvdc-lab simulate-all --output-dir reports/scenario-run
```

Each scenario produces:

- `<scenario>_telemetry.csv`: time-series snapshots
- `<scenario>_events.json`: scenario definition, command/injection event log, and final snapshot
