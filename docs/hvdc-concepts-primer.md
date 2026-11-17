# HVDC Concepts Primer for a Software Beginner

This is the minimum power-system vocabulary needed to understand the simulator. It is not an HVDC design, protection, or converter-engineering course.

## 1. What is an HVDC transmission link?

HVDC means **high-voltage direct current**. It is used to transmit electrical power as DC between converter stations. In a common two-terminal arrangement:

1. The sending-end converter station converts incoming AC power to DC.
2. A DC transmission path carries the power.
3. The receiving-end converter station converts DC power back to AC for the receiving network.

A converter station includes substantial power-electronic equipment, control and protection systems, measurements, communication, cooling, and auxiliaries. The project models two stations as abstract endpoints called `STATION-A` and `STATION-B`; it does not model semiconductor valves or AC/DC conversion physics.

Hitachi Energy publicly describes converter stations as converting electricity between AC and DC using high-power semiconductor valves. Its MACH overview describes a wider computerized control-and-protection platform with station control/monitoring servers, operator workstations, control/protection computers, DSP units, I/O systems, and valve-control units. This project is only a tiny training abstraction of supervisory software around that kind of system.

## 2. LCC and VSC — know the words, do not model them here

Two broad HVDC converter families you will encounter are:

- **LCC (Line-Commutated Converter):** uses thyristor-based converter technology and depends on the connected AC system for commutation.
- **VSC (Voltage-Source Converter):** uses controllable semiconductor valves and can provide different control capabilities from LCC schemes.

You do not need to implement either converter to complete this repository. The simulator deliberately abstracts the station internals. The job posting names HVDC as an advantage, so your first objective is to understand the architecture and vocabulary, not to claim converter-design expertise.

## 3. Separate three kinds of software responsibility

These terms are related but should not be mixed together:

| Area | Plain-language purpose | What this lab does |
|---|---|---|
| Control | Regulates quantities such as active power, current, voltage, and operating modes | Uses a simple supervisory power setpoint and a ramped toy value; it is not a real converter control loop |
| Protection | Detects abnormal or fault conditions and initiates a defined protective response | Demonstrates invented thresholds, time delays, alarm indications, and a latched training trip |
| Supervision and communication | Presents plant status, measurements, alarms, events, and operator requests; exchanges information with other systems | This is the main scope: state, telemetry, command interlocks, acknowledgements, OPC UA, and evidence |

The lab's simulated trip is not a protection relay algorithm. Do not use its thresholds, delays, or behavior in actual equipment.

## 4. Understand the dummy electrical values

The model uses the simple DC power relation:

\[
P = V \times I
\]

For DC quantities in the units used by this project:

\[
\text{MW} = \text{kV} \times \text{kA}
\]

Example:

- DC voltage = 400 kV
- DC current = 2.25 kA
- Simplified active power = 400 × 2.25 = 900 MW

This relation helps make the dummy data internally understandable. A real HVDC system has losses, converter behavior, measurement/control details, and operating constraints that this toy model ignores.

### Project's synthetic defaults

| Signal / parameter | Default or limit | Meaning in the exercise |
|---|---:|---|
| `dc_voltage_kv` | 400 kV | Nominal dummy DC voltage |
| `requested_power_mw` | 900 MW | Operator's requested training setpoint |
| `active_power_mw` | Starts at 0 MW | Simulated output ramps toward the setpoint |
| `dc_current_ka` | Derived from P/V while running | Simplified DC current |
| `cooling_temperature_c` | 45 °C | Dummy cooling/thermal measurement |
| `communication_healthy` | `true` | Whether station communications are healthy |
| `sensor_quality_good` | `true` | Whether measurement quality is marked good |
| `telemetry_age_s` | 0 s | Age/freshness of the data |
| `station_a_ready`, `station_b_ready` | `true` | Simulated station permissives/readiness |

Every protection/alarm threshold is in `config/settings.json`; do not hide limits in code. Keeping settings separate helps teach configuration control and test traceability.

## 5. Learn the operator/supervisory vocabulary

- **Telemetry:** measurements and statuses arriving from a plant or subsystem.
- **Quality flag:** metadata telling the application whether a signal is valid. A number can look plausible but still have bad quality.
- **Stale data:** a signal that has not been updated within the configured freshness window.
- **Interlock/permissive:** a condition required before a command is accepted. In this project Start requires healthy communications, good measurement quality, fresh telemetry, and both station-ready flags.
- **Alarm:** an abnormal condition that should be visible to an operator. It does not always trigger a trip.
- **Trip:** a defined transition to a latched state in this toy model. Reset is rejected until the active fault clears.
- **Event:** a time-stamped record of a command, rejection, injection, or trip for later investigation.
- **Acknowledge/handshake:** the protocol response telling a client whether a request was accepted and what the current state is.

## 6. Why the software lab uses OPC UA

OPC UA gives you a concrete way to practise an industrial communication interface without buying a PLC, I/O rack, or converter hardware. The server exposes an address space with typed variables grouped into `Telemetry`, `Status`, and `Control`. A client reads measurements/status and writes selected request nodes.

This does not mean OPC UA is the only protocol used in HVDC projects, or that it is the same as EtherCAT. EtherCAT is a different industrial Ethernet technology with master/slave cyclic process data and real-time synchronization concerns. The posting says EtherCAT **or other industrial communication protocols** are useful; implementing OPC UA demonstrates one real industrial protocol, while the EtherCAT note introduces the separate vocabulary.

## 7. Suggested learning order

1. Understand AC vs DC, converter stations, LCC/VSC, and the two-terminal link.
2. Learn voltage, current, power, units, measurement quality, and data freshness.
3. Distinguish control, protection, and supervision.
4. Learn states, alarms, events, interlocks, and command acknowledgements.
5. Run the simulator and trace one normal sequence and one fault sequence.
6. Browse the OPC UA address space and practise a client read/write handshake.
7. Read about EtherCAT after OPC UA makes sense; compare their communication roles instead of treating them as interchangeable.

## 8. Public further reading

- [Hitachi Energy — HVDC / MACH control and protection system](https://www.hitachienergy.com/products-and-solutions/hvdc/mach-control-and-protection-system)
- [Hitachi Energy — HVDC converter station overview](https://www.hitachienergy.com/products-and-solutions/hvdc)
- [OPC Foundation — OPC UA overview](https://opcfoundation.org/about/opc-technologies/opc-ua/)
- [EtherCAT Technology Group — EtherCAT technology](https://www.ethercat.org/en/technology.html)

## 9. What you should be able to explain after this primer

You should be able to explain, in plain English, what two converter stations do, why a supervisory system needs trustworthy measurements and communications, how an operator command can be rejected by an interlock, how an alarm differs from a trip, why the project uses OPC UA, and why none of these exercises makes the simulator a real HVDC control/protection system.
