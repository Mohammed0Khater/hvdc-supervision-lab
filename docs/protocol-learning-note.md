# Industrial Communication Learning Note

## What this project implements

The project implements a small local **OPC UA** server/client exercise. OPC UA is used here as an industrial interoperability interface: the server publishes typed measurements and status variables and exposes a small set of writable request nodes. This is useful for learning namespaces, address spaces, data types, reads/writes, client/server roles, and command acknowledgement.

## How EtherCAT differs

EtherCAT is an industrial Ethernet fieldbus designed for fast, synchronized I/O and motion/control communication. It is commonly used between a master and distributed slaves. It is not simply another name for OPC UA:

| Topic | OPC UA in this lab | EtherCAT |
|---|---|---|
| Typical role | Supervisory data exchange and semantic information modelling | Deterministic field-level cyclic process-data exchange |
| Main structure | Client/server address space and variables | Master/slave network with process data |
| Learning focus | Namespace, nodes, data types, read/write, session/security | Master configuration, slave identity, PDO mapping, cycle time, distributed clocks |
| Hardware needed here | None; loopback simulator | Real master/slave hardware for meaningful physical-bus practice, or a dedicated software/hardware test setup |
| Implemented by this repository | Yes, local training server/client | No |

## Further learning sequence

1. Understand client/server, endpoint, namespace, NodeId, data type, subscription, session, and secure channel in OPC UA.
2. Browse this project's address space and inspect read-only vs writable nodes.
3. Use Wireshark to inspect a local OPC UA session. Do not capture traffic from a company or operational network.
4. Read about EtherCAT master/slave architecture, process data objects, distributed clocks, cycle time, and topology.
5. Only after the basics, investigate an open-source EtherCAT master stack such as SOEM in an isolated Linux lab with suitable compatible hardware. Do not assume a virtual OPC UA test is EtherCAT experience.

## Vocabulary

- **Telemetry:** measurements and status published by the system.
- **Data quality:** indication that a value is valid/usable, not merely that a numeric value exists.
- **Stale data:** a value whose age exceeds the application's allowed freshness window.
- **Interlock:** a condition that must be satisfied before a command is accepted.
- **Alarm:** an operator-facing abnormal condition; not every alarm is a trip.
- **Trip:** a protective transition that latches a cause and moves the model to its tripped state.
- **FAT:** Factory Acceptance Test, typically performed before delivery; in this project only rehearsed in a virtual/software-only form.
- **SAT:** Site Acceptance Test; real SAT work requires approved project procedures and authorized personnel.
