# Architecture / Engineering Decision Log

| ID | Decision | Rationale | Consequence / limitation |
|---|---|---|---|
| ADR-001 | Use Python for the simulator and tests | Accessible for an entry-level learner; strong testing ecosystem | Not representative of every industrial target language or real-time runtime |
| ADR-002 | Use OPC UA as the implemented industrial protocol | Open, inspectable client/server interface with typed nodes | Does not provide EtherCAT bus practice or prove MACH interoperability |
| ADR-003 | Use deterministic scenario files | Repeatable verification and regression evidence | Not a physical or high-fidelity plant model |
| ADR-004 | Keep all endpoints on loopback | Avoid accidental network exposure | No multi-host deployment demonstration |
| ADR-005 | Use GitHub Actions for free hosted CI and AWS buildspec for CodeBuild familiarity | Free public-repository CI plus a reusable AWS build definition | GitHub Actions is not Azure DevOps; CodeBuild local agent runs build phase only |
| ADR-006 | Use synthetic limits and a simplified state machine | Safe educational scope | Cannot be used for real engineering design, commissioning, or protection settings |
