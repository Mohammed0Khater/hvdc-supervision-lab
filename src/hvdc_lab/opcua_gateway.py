"""Local OPC UA gateway for the training simulator.

The endpoint binds to 127.0.0.1 by default. Do not expose this demo server to a
network: it has no production identity, certificate, or authorization design.
"""

from __future__ import annotations

import asyncio
from typing import Any

from asyncua import Server

from .engine import PlantSimulator
from .scenarios import load_settings

NAMESPACE_URI = "urn:training:hvdc-supervision-lab"


async def run_server(
    endpoint: str = "opc.tcp://127.0.0.1:4840/hvdc-lab/",
    tick_seconds: float = 1.0,
) -> None:
    server = Server()
    await server.init()
    server.set_endpoint(endpoint)
    server.set_server_name("HVDC Supervision Lab - Training Simulator")
    namespace_index = await server.register_namespace(NAMESPACE_URI)

    root = await server.nodes.objects.add_object(namespace_index, "HVDCLink")
    telemetry_group = await root.add_object(namespace_index, "Telemetry")
    status_group = await root.add_object(namespace_index, "Status")
    control_group = await root.add_object(namespace_index, "Control")

    async def variable(parent: Any, name: str, initial: Any, writable: bool = False) -> Any:
        node = await parent.add_variable(namespace_index, name, initial)
        if writable:
            await node.set_writable()
        return node

    telemetry_nodes = {
        "dc_voltage_kv": await variable(telemetry_group, "DcVoltageKV", 400.0),
        "dc_current_ka": await variable(telemetry_group, "DcCurrentKA", 0.0),
        "active_power_mw": await variable(telemetry_group, "ActivePowerMW", 0.0),
        "cooling_temperature_c": await variable(telemetry_group, "CoolingTemperatureC", 45.0),
        "communication_healthy": await variable(telemetry_group, "CommunicationHealthy", True),
        "sensor_quality_good": await variable(telemetry_group, "SensorQualityGood", True),
        "telemetry_age_s": await variable(telemetry_group, "TelemetryAgeSeconds", 0.0),
    }
    status_nodes = {
        "state": await variable(status_group, "OperatingState", "STANDBY"),
        "trip_latched": await variable(status_group, "TripLatched", False),
        "trip_cause": await variable(status_group, "TripCause", ""),
        "active_alarms": await variable(status_group, "ActiveAlarms", ""),
        "last_command_message": await variable(status_group, "LastCommandMessage", "Server ready"),
        "last_command_accepted": await variable(status_group, "LastCommandAccepted", True),
    }
    control_nodes = {
        "start_request": await variable(control_group, "StartRequest", False, True),
        "stop_request": await variable(control_group, "StopRequest", False, True),
        "reset_trip_request": await variable(control_group, "ResetTripRequest", False, True),
        "requested_power_mw": await variable(control_group, "RequestedPowerMW", 900.0, True),
    }

    simulator = PlantSimulator(load_settings())
    await server.start()
    print(f"OPC UA server listening at {endpoint}")
    print(f"Namespace URI: {NAMESPACE_URI} (index {namespace_index})")
    print(
        "Use UAExpert or the bundled hvdc-lab opcua-client command to browse "
        "and issue simulated commands."
    )
    print(
        "Safety boundary: local training simulation only; "
        "endpoint is not hardened for network use."
    )
    last_requested_power = simulator.requested_power_mw

    try:
        while True:
            requested_power = float(await control_nodes["requested_power_mw"].read_value())
            if requested_power != last_requested_power:
                result = simulator.set_setpoint(requested_power)
                last_requested_power = requested_power if result.accepted else last_requested_power
                await status_nodes["last_command_accepted"].write_value(result.accepted)
                await status_nodes["last_command_message"].write_value(result.message)

            if await control_nodes["start_request"].read_value():
                result = simulator.start()
                await control_nodes["start_request"].write_value(False)
                await status_nodes["last_command_accepted"].write_value(result.accepted)
                await status_nodes["last_command_message"].write_value(result.message)
            if await control_nodes["stop_request"].read_value():
                result = simulator.stop()
                await control_nodes["stop_request"].write_value(False)
                await status_nodes["last_command_accepted"].write_value(result.accepted)
                await status_nodes["last_command_message"].write_value(result.message)
            if await control_nodes["reset_trip_request"].read_value():
                result = simulator.reset_trip()
                await control_nodes["reset_trip_request"].write_value(False)
                await status_nodes["last_command_accepted"].write_value(result.accepted)
                await status_nodes["last_command_message"].write_value(result.message)

            snapshot = simulator.tick(tick_seconds)
            for key, node in telemetry_nodes.items():
                await node.write_value(snapshot[key])
            for key, node in status_nodes.items():
                value = snapshot[key] if key in snapshot else None
                if key == "active_alarms":
                    value = ";".join(snapshot["active_alarms"])
                if value is not None:
                    await node.write_value(value)
            await asyncio.sleep(tick_seconds)
    finally:
        await server.stop()


async def send_command(
    endpoint: str,
    command: str,
    power_mw: float | None = None,
) -> None:
    from asyncua import Client

    async with Client(url=endpoint) as client:
        namespace_index = await client.get_namespace_index(NAMESPACE_URI)

        async def node(group: str, name: str) -> Any:
            return await client.nodes.root.get_child(
                f"0:Objects/{namespace_index}:HVDCLink/"
                f"{namespace_index}:{group}/{namespace_index}:{name}"
            )

        if power_mw is not None:
            await (await node("Control", "RequestedPowerMW")).write_value(float(power_mw))
            print(f"Wrote RequestedPowerMW={power_mw}")
        command_nodes = {
            "start": "HVDCLink.Control.StartRequest",
            "stop": "HVDCLink.Control.StopRequest",
            "reset": "HVDCLink.Control.ResetTripRequest",
        }
        if command not in command_nodes and command != "setpoint":
            raise ValueError("command must be start, stop, reset, or setpoint")
        if command in command_nodes:
            group, name = command_nodes[command].split(".")[-2:]
            await (await node(group, name)).write_value(True)
            print(f"Wrote {command} request")
        await asyncio.sleep(1.2)
        for label, identifier in [
            ("Operating state", "HVDCLink.Status.OperatingState"),
            ("Last command accepted", "HVDCLink.Status.LastCommandAccepted"),
            ("Last command message", "HVDCLink.Status.LastCommandMessage"),
        ]:
            group, name = identifier.split(".")[-2:]
            print(f"{label}: {await (await node(group, name)).read_value()}")
