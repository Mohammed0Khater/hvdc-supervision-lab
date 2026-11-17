# Verification Record — Template

- Project: HVDCLAB-001
- Software revision / Git commit:
- Configuration revision:
- Test date (UTC):
- Tester:
- Python version:
- Operating system:

## Automated test results

| Test command | Result (PASS/FAIL) | Evidence path | Notes |
|---|---|---|---|
| `ruff check src tests` | | | |
| `pytest -q` | | | |
| `hvdc-lab simulate-all --output-dir reports/run-YYYYMMDD` | | | |

## OPC UA integration results

| Check | Expected | Actual | Result | Evidence |
|---|---|---|---|---|
| Endpoint connection | Client connects to loopback endpoint | | | |
| Browse | `HVDCLink/Telemetry`, `Status`, `Control` visible | | | |
| Telemetry read | Voltage/current/power return numeric values | | | |
| Start handshake | Start request consumed; acceptance/status updated | | | |
| Stop handshake | State returns to STANDBY | | | |
| Interlock | Communication unhealthy causes start rejection | | | |

## Defects and deviations

| Defect ID | Description | Severity | Disposition | Retest evidence |
|---|---|---|---|---|

## Conclusion

State whether the tested revision meets the training project's acceptance criteria. Clearly list any untested behavior and known limitations.
