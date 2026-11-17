# Software Verification Test Plan

## 1. Objective

Verify that the training supervisory application accepts valid commands, rejects invalid commands, generates expected alarms, latches selected synthetic trips, and exposes its interface data in a repeatable manner.

## 2. Test levels

| Level | Method | Purpose |
|---|---|---|
| Unit | pytest against `PlantSimulator` | Validate individual state, command, and alarm behaviors |
| Scenario regression | Run JSON scenarios | Confirm known fault sequences remain reproducible |
| Interface integration | OPC UA client/server session | Confirm browse, read, write, command acknowledgement, and telemetry update |
| Static checks | Ruff | Catch common style and correctness problems |
| CI verification | GitHub Actions and AWS CodeBuild-compatible buildspec | Ensure the same checks run after changes |
| Virtual FAT exercise | Execute commissioning checklist against simulator | Rehearse evidence capture and expected/actual comparison |

## 3. Test cases

| Test ID | Scenario | Action | Expected result |
|---|---|---|---|
| UT-001 | Normal command | Start from healthy STANDBY | Start accepted; state becomes RUNNING |
| UT-002 | Communication unhealthy | Request start with communication flag false | Request rejected; state remains STANDBY |
| UT-003 | DC overvoltage | Inject 455 kV and advance through configured delay | `DC_OVERVOLTAGE` trip latches |
| UT-004 | DC overcurrent | Inject 3.5 kA and advance through configured delay | `DC_OVERCURRENT` trip latches |
| UT-005 | Trip reset while fault active | Request reset while overvoltage remains | Reset rejected |
| UT-006 | Trip reset after fault clears | Remove synthetic fault and request reset | Reset accepted; state returns to STANDBY |
| UT-007 | Cooling warning | Inject 85 °C | High-temperature alarm active; no trip |
| UT-008 | Bad measurement quality | Inject BAD quality for configured delay | Quality alarm and `BAD_MEASUREMENT_QUALITY` trip |
| UT-009 | Out-of-range setpoint | Request 1,200 MW | Command rejected; accepted setpoint unchanged |
| UT-010 | Clear a test injection | Inject changed signals, then clear injection | Original signal values restored |
| UT-011 | Station readiness | Set Station B not ready, then request start | Start rejected; state remains STANDBY |
| UT-012 | Normal stop | Start, then issue stop | State returns to STANDBY and simulated power becomes zero |
| UT-013 | Stale telemetry | Inject age beyond the freshness limit | Stale alarm appears, then `STALE_TELEMETRY` trip latches after the synthetic delay |
| SC-001 | Normal start | Execute `normal.json` | No trip; link ends RUNNING |
| SC-002 | Communication loss | Execute `communication_loss.json` | Communication alarm and latched trip |
| SC-003 | Startup interlock | Communication unhealthy before start | Start rejected |
| SC-004 | Stale telemetry | Inject 5-second telemetry age after Start | Stale alarm and delayed trip |
| IT-001 | OPC UA browse/read | Browse `HVDCLink` and read telemetry | Documented nodes are visible and typed correctly |
| IT-002 | OPC UA command | Write `RequestedPowerMW`, then `StartRequest` | Request is consumed and acknowledgement/status update |

## 4. Entry criteria

- Project dependencies installed in an isolated virtual environment.
- Configuration revision and scenario files are identified.
- No live endpoint, device, credential, or customer data is configured.

## 5. Exit criteria

- All automated tests pass.
- All scenarios produce CSV and JSON evidence.
- OPC UA manual checks are recorded in the verification record.
- Any failure has a reproducible defect record with expected and actual behavior.
- Known limitations are documented before creating a release tag.

## 6. Evidence retention

Retain the source revision, configuration file, scenario JSON, test output, generated CSV, event JSON, and a short verification record together. Do not edit test evidence to make a result look successful; rerun the test after a fix and retain the new result.
