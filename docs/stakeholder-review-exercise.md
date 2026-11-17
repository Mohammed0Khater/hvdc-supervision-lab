# Cross-Functional Review Exercise — Fictional Roles

This is a practice worksheet. No actual stakeholder has reviewed or approved this repository.

| Reviewer role | Example review comment | Your response / design decision | Evidence to update |
|---|---|---|---|
| Control & Protection | Should a reset be allowed while the overvoltage measurement remains above the trip threshold? | No. Reset is rejected while any trip cause is still active. | UT-005, test plan, state diagram |
| IT/OT | Can writable command nodes be exposed to a corporate network? | No. The demo binds to loopback; production security and network design are outside the project. | ICD, safety note |
| Hardware | What happens if sensor quality is BAD even though the raw value is plausible? | The quality flag is treated separately from numeric range and causes an alarm/trip after the synthetic delay. | UT-008, interface document |
| Operations | How can an operator tell whether a start request succeeded? | The client checks acceptance flag, acknowledgement text, and operating state. | ICD command handshake |

## Review record format

- Date:
- Software/configuration revision:
- Participants (role-play only unless real reviewers are involved):
- Topic:
- Comment:
- Decision:
- Rationale:
- Follow-up issue:
- Documents/tests changed:
