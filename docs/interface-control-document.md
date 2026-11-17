# Interface Control Document (ICD) — Local OPC UA Interface

## 1. Endpoint

- Default endpoint: `opc.tcp://127.0.0.1:4840/hvdc-lab/`
- Namespace URI: `urn:training:hvdc-supervision-lab`
- Transport: OPC UA TCP, local loopback only
- Authentication/security: deliberately simplified for local training; no production certificate, user identity, role model, or network security configuration is implemented.

## 2. Address-space structure

```text
Objects
└── HVDCLink
    ├── Telemetry
    │   ├── DcVoltageKV                 Float / read-only
    │   ├── DcCurrentKA                 Float / read-only
    │   ├── ActivePowerMW               Float / read-only
    │   ├── CoolingTemperatureC         Float / read-only
    │   ├── CommunicationHealthy       Boolean / read-only
    │   ├── SensorQualityGood           Boolean / read-only
    │   └── TelemetryAgeSeconds         Float / read-only
    ├── Status
    │   ├── OperatingState              String / read-only
    │   ├── TripLatched                 Boolean / read-only
    │   ├── TripCause                   String / read-only
    │   ├── ActiveAlarms                String / read-only, semicolon-separated
    │   ├── LastCommandAccepted         Boolean / read-only
    │   └── LastCommandMessage          String / read-only
    └── Control
        ├── StartRequest               Boolean / writable request bit
        ├── StopRequest                Boolean / writable request bit
        ├── ResetTripRequest           Boolean / writable request bit
        └── RequestedPowerMW           Float / writable setpoint
```

## 3. Command handshake

1. Client writes a request bit or changes `RequestedPowerMW`.
2. Server reads the request during its next scan.
3. Server applies the supervisory preconditions and command validation.
4. The server clears the request bit after consuming it.
5. Server updates `LastCommandAccepted` and `LastCommandMessage`.
6. Client reads the response and checks `OperatingState`, `TripLatched`, and relevant telemetry.

The Boolean request tags are not a hard real-time command channel. They are a simple training handshake only.

## 4. Data types and units

| Signal | Type | Unit / meaning |
|---|---|---|
| `DcVoltageKV` | Float | kV, synthetic DC voltage measurement |
| `DcCurrentKA` | Float | kA, synthetic DC current measurement |
| `ActivePowerMW` | Float | MW, simulated active power |
| `CoolingTemperatureC` | Float | degrees Celsius, synthetic temperature |
| `CommunicationHealthy` | Boolean | Simulated communication link health |
| `SensorQualityGood` | Boolean | Simulated data-quality flag |
| `TelemetryAgeSeconds` | Float | Age of measurement data in seconds |
| `OperatingState` | String | STANDBY, RUNNING, TRIPPED |
| `TripLatched` | Boolean | Whether a simulated trip is latched |
| `TripCause` | String | Machine-readable cause code |

## 5. Error handling

- Rejected commands do not change the operating state.
- Rejected commands update the text acknowledgement.
- A reset is rejected while a trip condition remains active.
- A client disconnect does not imply that the simulated station is safe or stopped; the model has its own communication-health flag.

## 6. Security boundary

Do not bind this endpoint to `0.0.0.0`, forward port 4840, or connect it to a real device/network. Before using OPC UA outside an isolated lab, learn application certificates, trust lists, secure channel policies, user authentication, role permissions, network segmentation, logging, and change control. This project is not a hardened OPC UA server.
