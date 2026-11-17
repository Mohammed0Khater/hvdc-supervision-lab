# Safety, Integrity, and Data Handling

## Non-negotiable boundary

This repository is a software-only educational simulation. It must never be connected to an energized HVDC link, substation network, relay, PLC, converter controller, RTU, protection IED, or production OT environment. Do not use the thresholds, commands, or logic as real protection/control settings.

## Main hazards considered

| Hazard | Cause in a real environment | Training-lab control |
|---|---|---|
| Unintended plant operation | A software command reaches a real actuator | No physical I/O drivers; OPC UA endpoint binds to loopback only |
| Incorrect protection behavior | Unvalidated thresholds or logic | Synthetic values explicitly labelled; no safety claim; tests are educational |
| Unauthorized command | Unauthenticated writable protocol node | Local-only endpoint; never expose port 4840; production security deliberately out of scope |
| Misleading engineering claim | Portfolio overstates what was built | README explicitly distinguishes simulator, protocol exercise, and proprietary MACH platform |
| Confidentiality breach | Customer tags, addresses, or credentials committed | Use synthetic tags only; never commit secrets or employer material |
| Incorrect evidence | Test report edited or generated from stale code | Record Git commit and config revision; rerun tests after code/config changes |

## Integrity rules

1. Never copy Hitachi Energy proprietary material, screenshots, configuration, code, or internal process documentation into this repository.
2. Do not use EEHC station information, equipment identifiers, protection settings, photographs, or internal documents.
3. Use generic, invented plant identifiers and test values only.
4. Record assumptions and unknowns instead of presenting guesses as facts.
5. A failed test is engineering evidence, not something to hide. File a defect and retest after the correction.
6. Do not claim the project demonstrates MACH proficiency, real-time deterministic performance, safety-certified protection, EtherCAT implementation, or field commissioning.

## Stop conditions

Stop the exercise if a step asks you to connect to a live IP address, use a real control network, scan a corporate/substation network, write to a physical device, or enter an employer's credentials or data. None of those activities are necessary for this project.
