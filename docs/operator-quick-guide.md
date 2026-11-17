# Operator Quick Guide — Training Simulator

## Start the server

```powershell
python -m hvdc_lab opcua-server
```

The server listens on `opc.tcp://127.0.0.1:4840/hvdc-lab/`.

## Send commands from a second terminal

```powershell
# Set a target before starting
python -m hvdc_lab opcua-client --command setpoint --power-mw 850

# Start
python -m hvdc_lab opcua-client --command start

# Stop
python -m hvdc_lab opcua-client --command stop

# Reset a trip only after its injected fault is cleared
python -m hvdc_lab opcua-client --command reset
```

## Browse using UAExpert

1. Open UAExpert and add a server endpoint: `opc.tcp://127.0.0.1:4840/hvdc-lab/`.
2. Connect using the default local-demo configuration.
3. Browse Objects → HVDCLink.
4. Drag telemetry/status variables into the Data Access View.
5. For a command exercise, write `RequestedPowerMW` or set one request bit under Control.
6. Watch `LastCommandAccepted`, `LastCommandMessage`, and `OperatingState` update.

## Stop

Press `Ctrl+C` in the terminal running the OPC UA server. If the process does not exit cleanly, stop the process from the terminal. Do not terminate or alter any other application based on this project.

## Important

The writable tags control only the Python simulation. They must never be redirected to an industrial device or real OT network.
