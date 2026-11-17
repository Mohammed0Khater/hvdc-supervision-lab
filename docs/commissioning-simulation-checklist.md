# Virtual Commissioning / FAT-SAT Rehearsal Checklist

> Training-only. This is a desk-based software verification exercise against a simulator. It is not a site commissioning procedure and must not be used to energize or operate equipment.

## A. Document and configuration checks

- [ ] Confirm project identifier `HVDCLAB-001`.
- [ ] Confirm Git commit hash and software version.
- [ ] Confirm configuration file revision and scenario set.
- [ ] Confirm no production IP address, credential, customer data, or physical I/O device is present.
- [ ] Confirm the endpoint is `127.0.0.1` only.

## B. Software readiness

- [ ] Install project into a clean virtual environment.
- [ ] Run `ruff check src tests`.
- [ ] Run `pytest -q`.
- [ ] Run `hvdc-lab simulate-all --output-dir reports/commissioning`.
- [ ] Review generated CSV and JSON reports.

## C. Interface checks

- [ ] Start the local OPC UA server.
- [ ] Connect using UAExpert or the bundled command-line client.
- [ ] Browse Telemetry, Status, and Control nodes.
- [ ] Confirm telemetry is read-only.
- [ ] Change the requested power setpoint within the synthetic range and inspect acknowledgement.
- [ ] Send StartRequest and confirm RUNNING.
- [ ] Send StopRequest and confirm STANDBY.
- [ ] Inject a communication-unhealthy scenario through the simulator and confirm a start request is rejected.

## D. Fault scenario checks

- [ ] DC overvoltage: confirm alarm, configured delay, trip latch, and rejected reset while the fault remains.
- [ ] DC overcurrent: confirm the expected cause code.
- [ ] Communication loss: confirm alarm and trip behavior.
- [ ] Bad measurement quality: confirm quality alarm and configured response.
- [ ] Cooling warning: confirm alarm without trip below the synthetic trip threshold.

## E. Closeout

- [ ] Complete the verification record.
- [ ] File issues for unexpected behavior; do not silently change the expected result.
- [ ] Update documentation and traceability if a requirement or interface changed.
- [ ] Tag only a revision whose automated tests and scenario regressions pass.

## Difference from real site commissioning

Real commissioning may include safety permits, isolation and switching plans, hardware inspections, wiring and I/O checks, protection tests, network and time-synchronization checks, control sequence tests, interlocks, customer witness points, rollback planning, and formal handover. This project rehearses only the software/documentation mindset and a virtual protocol check. Site activities are performed only by authorized personnel under approved project procedures.
