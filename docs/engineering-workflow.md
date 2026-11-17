# Engineering Workflow and Team Simulation

This workflow is a practical approximation of common industrial software-engineering discipline derived from the public role description. It is not a disclosure or claim about Hitachi Energy's internal work instructions.

## 1. Backlog and requirements

Use GitHub Issues as a lightweight work-item tracker. Each work item should include:

- requirement ID(s)
- objective and reason
- scope / non-scope
- acceptance criteria written so they can be tested
- dependencies and stakeholder input required
- verification evidence to attach

Create GitHub milestone `v0.1 - Supervisory demonstrator` and group the following work items:

1. Document operating states and command preconditions.
2. Implement deterministic plant/signal model.
3. Implement alarms and latched trip behavior.
4. Expose telemetry and command nodes through OPC UA.
5. Add unit and scenario regression tests.
6. Add CI, buildspec, interface document, and test record.
7. Complete the virtual FAT rehearsal and release baseline.

## 2. Branching model

- `main`: tested baseline only.
- `feature/<issue-number>-short-name`: one coherent task per branch.
- `fix/<issue-number>-short-name`: one defect correction per branch.

Example:

```powershell
git switch -c feature/12-add-comms-alarm
# make a small change
git add src tests docs
git commit -m "feat: add communication health alarm"
git push -u origin feature/12-add-comms-alarm
```

Open a Pull Request against `main`, reference the Issue, summarize the behavior change, include test output, and update the traceability matrix. Do not merge a failed test or a change with undocumented threshold/interface changes.

## 3. Definition of done

A task is done only when:

- implementation is complete and reviewed by you against its acceptance criteria
- automated tests pass
- relevant fault scenario has been run
- docs/interface/traceability are updated
- no secrets or employer data are included
- the PR explains limitations and outstanding risks

For solo practice, self-review is not equivalent to independent peer review, and role-play is not real teamwork. Record it as a self-review and ask a knowledgeable engineer to review the design when such a person is available.

## 4. Simulated cross-functional design review

Use these fictional review prompts to practice discussing interface boundaries:

| Stakeholder role | Review prompt | What you should record |
|---|---|---|
| Control & Protection engineer | What is the required operating-state behavior when a trip is latched? | State transition, trip cause, reset preconditions, test reference |
| IT/OT engineer | Which nodes are read-only, which are writable, and what security boundary applies? | Node map, command handshake, certificate/authentication gaps |
| Hardware engineer | What does the simulator assume about measurement validity and station readiness? | Signal list, units, quality flags, unavailable hardware behavior |
| Operations / commissioning engineer | What evidence proves that the expected sequence was exercised? | Test record, alarm/event timeline, known limitations |

These are fictional exercises, not real consultations or endorsements. Write a short review log containing comment, decision, rationale, owner, and follow-up Issue ID.

## 5. Asking for support and escalation

When blocked, create a concise issue with:

1. what you expected
2. what actually happened
3. smallest reproducible example
4. logs / test output
5. what you have already tried
6. the specific decision or expertise you need

Do not hide an uncertain assumption in code. Record it in `docs/decisions/` or the relevant issue and ask for review before treating it as a requirement.

## 6. Release and configuration baseline

After all tests pass:

```powershell
git switch main
git pull
git tag -a v0.1.0 -m "Training demonstrator baseline v0.1.0"
git push origin v0.1.0
```

Attach the exact commit hash, configuration revision, scenario outputs, and verification record to the release notes. If a test is rerun after code changes, create a new evidence set rather than overwriting historical evidence.
