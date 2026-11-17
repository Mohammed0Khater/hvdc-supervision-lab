# Beginner Walkthrough — From First Launch to an Engineering Release

This document tells you what to do after installing the prerequisites in the root README. Work in order. Do not skip straight to GitHub or OPC UA: first understand what the simulator represents and what its limitations are.

## Before touching code: the five ideas

1. **A plant signal** is a measurement or status value, such as DC voltage, DC current, cooling temperature, or a station-ready flag.
2. **A supervisory state** is the high-level status of the link in this toy model: `STANDBY`, `RUNNING`, or `TRIPPED`.
3. **An interlock** is a precondition that rejects a command when the system is not ready. This project checks communication health, measurement quality, data freshness, and both station-ready flags before accepting Start.
4. **An alarm** tells an operator that a condition is abnormal. A **trip** is a separate latched state transition in this training model. An alarm does not always mean a trip.
5. **Verification evidence** is the proof that a requirement was tested: test output, telemetry CSV, event JSON, and a completed verification record.

These are learning abstractions. The thresholds and logic are invented and must never be copied into a real protection or control system.

## Session 1 — Open the code in the right place

1. Extract the archive to a normal folder, for example `C:\Users\YOUR_USER\Projects\hvdc-supervision-lab`.
2. Open Visual Studio Code.
3. Select **File → Open Folder** and choose the `hvdc-supervision-lab` folder. Select the folder containing `pyproject.toml`, not its parent and not `src`.
4. In VS Code, select **Terminal → New Terminal**. The prompt should end in `hvdc-supervision-lab`.
5. Run:

```powershell
py -3.13 --version
git --version
```

If either command fails, fix that installation before continuing. Do not try to install project dependencies from the wrong folder.

## Session 2 — Create the Python environment and prove the baseline works

Run each command separately and read the output:

```powershell
py -3.13 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The prompt should show `(.venv)` after activation. The `-e` option installs this folder as an editable package, so code changes are reflected without reinstalling. The `[dev]` extra installs pytest, coverage, and Ruff. `asyncua` is the OPC UA library.

Now run:

```powershell
ruff check src tests
coverage run -m pytest -q
coverage report
```

Expected baseline: all 12 tests pass and the core simulator/scenario modules meet the 75% configured coverage gate. Coverage is not a quality score and does not prove the OPC UA integration works; it only reports which measured Python lines/branches the unit tests executed.

If PowerShell says the `hvdc-lab` command is not recognized later, verify that `(.venv)` is active and run `python -m hvdc_lab` instead.

## Session 3 — Read the implementation in this order

Open these files in VS Code and read them from top to bottom:

| File | What to learn |
|---|---|
| `config/settings.json` | Synthetic plant parameters, limits, and delays |
| `config/scenarios/normal.json` | Time-based input events for one simulation |
| `src/hvdc_lab/engine.py` | State, command acceptance/rejection, alarms, trip timers, snapshots |
| `src/hvdc_lab/scenarios.py` | Loading scenario files and exporting CSV/JSON |
| `src/hvdc_lab/cli.py` | How terminal commands are translated into Python function calls |
| `src/hvdc_lab/opcua_gateway.py` | The local OPC UA server, address space, and client writes |
| `tests/test_engine.py` | How expected behavior is expressed as automated tests |

Do not try to memorise the whole codebase. Your first goal is to be able to explain the data flow:

`scenario JSON → PlantSimulator → supervisory logic → snapshot → CSV + JSON evidence`

The OPC UA path is separate:

`OPC UA client → writable request node → server validates command → PlantSimulator → read-back acknowledgement/status`

## Session 4 — Run and inspect the normal operating case

```powershell
hvdc-lab list-scenarios
hvdc-lab simulate --scenario normal --output-dir reports/normal
```

Open `reports/normal/normal_telemetry.csv` in VS Code. The columns are the signal names and status values. Find the rows where `state` changes from `STANDBY` to `RUNNING`, and observe `active_power_mw` ramp towards the 900 MW training setpoint. Open `reports/normal/normal_events.json` and inspect the event list.

Answer these questions in your own notes:

- At what simulated second was Start accepted?
- What is the difference between `requested_power_mw` and `active_power_mw`?
- Why can requested power be 900 MW while actual simulated power is still ramping?
- What evidence would you show a reviewer to prove the state changed?

## Session 5 — Create your own fault scenario (first code/config change)

Create a new file named `config/scenarios/station_b_unavailable.json`. Paste this exact JSON:

```json
{
  "name": "Station B unavailable startup interlock",
  "description": "Station B is not ready when the operator requests startup.",
  "duration_s": 8,
  "step_s": 1,
  "events": [
    {"at_s": 1, "type": "inject", "values": {"station_b_ready": false}},
    {"at_s": 2, "type": "command", "command": "start"}
  ]
}
```

Save the file. Run:

```powershell
hvdc-lab list-scenarios
hvdc-lab simulate --scenario station_b_unavailable --output-dir reports/station_b_unavailable
```

Expected outcome: the state remains `STANDBY`; the command is rejected because Station B is not ready. Open the JSON event report and find the `COMMAND_REJECTED` entry. This is an example of a test input and expected output being made repeatable through configuration instead of manually changing code for each test.

Next, copy `config/scenarios/cooling_alarm.json` to `config/scenarios/cooling_trip.json`. Change the injected temperature from `85.0` to `98.0` and the description to say it should cross the training trip threshold. Run the new scenario. Expected outcome: `TRIPPED`, with `COOLING_OVERTEMPERATURE` as the cause. Compare the alarm-only 85 °C run to the trip-level 98 °C run.

## Session 6 — Add a test before changing engine behavior

Open `tests/test_engine.py`. Tests follow the arrange / act / assert pattern:

- Arrange: create a known simulator state.
- Act: call one method or run one scenario.
- Assert: compare the observed behavior with the requirement.

Add a test for the new Station B readiness scenario. At the top of the file, add `import json` if it is not already there. Then add:

```python
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
```

Run the single test first:

```powershell
python -m pytest tests/test_engine.py -q
```

Then run the full checks. If a test fails, do not edit the expected result just to make it pass. Read the failure, identify whether the code, scenario, or expectation is wrong, then correct the relevant item and rerun the test.

## Session 7 — Understand the OPC UA integration

Open two VS Code terminals. In terminal 1:

```powershell
.\.venv\Scripts\Activate.ps1
python -m hvdc_lab opcua-server
```

Leave it running. In terminal 2:

```powershell
.\.venv\Scripts\Activate.ps1
python -m hvdc_lab opcua-client --command setpoint --power-mw 850
python -m hvdc_lab opcua-client --command start
python -m hvdc_lab opcua-client --command stop
```

The server listens on `opc.tcp://127.0.0.1:4840/hvdc-lab/`. The loopback address means your demo is listening only on the same machine. It is not a secure production endpoint.

The OPC UA address space is documented in `docs/interface-control-document.md`. `Telemetry` and `Status` nodes are read-only; `Control` contains the explicit write-request nodes. The server consumes a request, checks it, clears the request bit, and publishes an acknowledgement. This request/acknowledgement pattern is central to the exercise.

If the server does not start, verify dependencies were installed into the active `.venv`, check whether port 4840 is already in use, and read the full traceback. Do not change the bind address to `0.0.0.0` to solve a local connection problem.

## Session 8 — Practise Git as an engineering tool

First initialise Git and create a baseline:

```powershell
git init -b main
git add .
git status
git commit -m "chore: initial HVDC supervision lab"
```

If Git says your identity is unknown, configure your own name and email (use the email associated with your GitHub account if you want commits linked to that account), then retry the commit:

```powershell
git config --global user.name "YOUR DISPLAY NAME"
git config --global user.email "YOUR_GITHUB_EMAIL"
```

Create a separate branch for your Station B feature:

```powershell
git switch -c feature/station-b-start-interlock
```

Make a small change, run the tests, then:

```powershell
git status
git diff
git add config tests docs
git commit -m "test: add station B readiness scenario"
```

`git diff` lets you inspect exactly what changed before committing. A commit should represent one understandable unit of work, not a random collection of unrelated edits.

## Session 9 — Publish and use pull requests

Create a **public** GitHub repository named `hvdc-supervision-lab`. Do not pre-create another README or `.gitignore`. Add the remote and push:

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/hvdc-supervision-lab.git
git push -u origin main
git push -u origin feature/station-b-start-interlock
```

Replace the placeholder with your username. On GitHub, open the feature branch and select **Compare & pull request**. Fill in the PR template: what changed, requirement ID, tests performed, evidence, and any limitations. Wait for the CI workflow to pass. Review the changed files and then merge the PR. For solo practice, call it a self-review; do not describe it as an independent peer review.

GitHub Issues / Projects are used for work items and a Kanban board. GitHub Actions runs the pipeline on pushes and pull requests. Standard hosted runners are free for public repositories. This is a practical free workflow, not Azure DevOps and not proof that Hitachi uses GitHub.

## Session 10 — Try AWS CodeBuild locally

The AWS-specific exercise is optional. The root README's Section 11 has the Docker Desktop + WSL2 installation sequence. Use the same project and its `buildspec.yml`; run the official CodeBuild local agent against an AWS CodeBuild image. This teaches the CodeBuild buildspec phases without an AWS account or cloud build minutes. It is not a full local CodePipeline or an Azure Boards clone. Keep GitHub as repository, issue/PR, and hosted CI service.

## Session 11 — Complete the engineering evidence pack

1. Open `docs/requirements-traceability.csv` and verify that each requirement still points to the correct source, test, and evidence location.
2. Open `docs/test-plan.md` and add your new scenario as a test case.
3. Run all automated tests and every scenario:

```powershell
ruff check src tests
coverage run -m pytest -q
coverage report
hvdc-lab simulate-all --output-dir reports/release-candidate
```

4. Complete `docs/verification-record-template.md`. Record the actual Python version, OS, Git commit, configuration revision, test commands and results. Do not claim an OPC UA check passed unless you actually ran it.
5. Work through `docs/commissioning-simulation-checklist.md`. This is a virtual software-only rehearsal, not a real FAT/SAT or site commissioning procedure.
6. Review `docs/safety-and-integrity.md` and `docs/stakeholder-review-exercise.md`.
7. Update `README.md` with any extra features you actually completed.
8. Tag your tested baseline:

```powershell
git switch main
git pull
git tag -a v0.2.0 -m "Station readiness scenario and verification update"
git push origin v0.2.0
```

Do not tag the release until tests and scenario results are green.

## Your completion test

You are ready to discuss this project in an interview only when you can do all of the following without merely reading the README aloud:

- Explain how a request travels from scenario JSON or OPC UA client to the simulator and back to a status acknowledgement.
- Explain the difference between a command interlock, alarm, and trip in this toy system.
- Modify a scenario, predict its expected result, run it, and locate the supporting event and telemetry evidence.
- Add a test for a new behavior and explain what the assertion proves.
- Trace a requirement to code, test, documentation, and a Git commit.
- Explain why the project uses OPC UA and why that does not mean EtherCAT was implemented.
- State clearly which parts are synthetic and why the repository is not a MACH or real protection system.
