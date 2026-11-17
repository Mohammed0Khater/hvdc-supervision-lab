# Project Charter — HVDCLAB-001

## Purpose

Build a small, testable software demonstrator for the supervisory and communication layer around a fictional two-terminal HVDC link. The deliverable is intended to teach software lifecycle practices relevant to an entry-level HVDC Control & Protection Software Engineer role: requirements, design, implementation, test, integration, verification, documentation, version control, and release evidence.

## System under study

- Link identifier: `TRAINING-LINK-01`
- Converter terminal abstractions: `STATION-A` and `STATION-B`
- Nominal DC voltage used in the synthetic model: 400 kV
- Demonstration power setpoint: 900 MW (maximum setpoint in this toy model: 1,000 MW)
- Supervisory interface: local OPC UA server
- Software implementation: Python
- Verification: pytest, deterministic scenarios, static checks, and manual OPC UA client checks

## In scope

1. Simulate supervisory state and selected plant telemetry.
2. Implement simulated start, stop, setpoint, and trip-reset request handling.
3. Enforce command preconditions using synthetic readiness, communication, and data-quality flags.
4. Generate alarms and latch selected simulated trip conditions using configurable synthetic thresholds and delays.
5. Publish telemetry, status, alarms, and writable command request tags over local OPC UA.
6. Produce CSV telemetry and JSON event evidence for repeatable scenarios.
7. Use Git branches, issues, pull requests, automated tests, GitHub Actions, and an AWS CodeBuild-compatible `buildspec.yml`.

## Out of scope

- Reproducing Hitachi Energy's MACH platform, libraries, engineering database, or development environment.
- Detailed EMT, MMC, LCC, converter valve, firing-pulse, or electromagnetic transient modelling.
- Real protection relay algorithms, grid-code compliance, functional safety certification, or protection coordination studies.
- Real EtherCAT master/slave communication or EtherCAT hardware.
- Connecting to an electricity substation, PLC, relay, converter, RTU, or any live operational network.
- Using the synthetic limits as engineering recommendations or as values for a real HVDC project.

## Success criteria

- A new user can install the project using the instructions in the root README.
- Automated tests pass locally and in GitHub Actions.
- Each fault scenario generates a reproducible report.
- The OPC UA server exposes documented nodes and accepts only the explicitly simulated commands.
- Each role requirement in `requirements-traceability.csv` points to a project artifact and verification method.
- Limitations are stated clearly and no actual Hitachi proprietary process is claimed.

## Configuration control

- Project baseline: `0.1.0`
- Configuration file: `config/settings.json`
- Scenario files: `config/scenarios/*.json`
- Any change to thresholds, interfaces, state transitions, or command behavior requires a test update and documentation update in the same pull request.
