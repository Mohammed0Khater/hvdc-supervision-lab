"""Command-line interface for the training lab."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .scenarios import list_scenarios, run_scenario


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hvdc-lab",
        description="Training-only HVDC supervisory simulator",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser(
        "list-scenarios",
        help="List the bundled synthetic test scenarios",
    )
    list_parser.set_defaults(handler=lambda _args: print("\n".join(list_scenarios())))

    sim = subparsers.add_parser(
        "simulate",
        help="Run a deterministic scenario and write CSV/JSON reports",
    )
    sim.add_argument("--scenario", required=True, choices=list_scenarios())
    sim.add_argument("--output-dir", type=Path, default=Path("reports"))
    sim.add_argument("--settings", type=Path, default=None)
    sim.set_defaults(handler=_run_simulation)

    all_sim = subparsers.add_parser("simulate-all", help="Run every bundled scenario")
    all_sim.add_argument("--output-dir", type=Path, default=Path("reports"))
    all_sim.set_defaults(handler=_run_all)

    server = subparsers.add_parser("opcua-server", help="Start the local OPC UA simulator server")
    server.add_argument("--endpoint", default="opc.tcp://127.0.0.1:4840/hvdc-lab/")
    server.add_argument("--tick-seconds", type=float, default=1.0)
    server.set_defaults(handler=_run_server)

    client = subparsers.add_parser(
        "opcua-client",
        help="Send a simulated command to the local OPC UA server",
    )
    client.add_argument("--endpoint", default="opc.tcp://127.0.0.1:4840/hvdc-lab/")
    client.add_argument("--command", required=True, choices=["start", "stop", "reset", "setpoint"])
    client.add_argument("--power-mw", type=float, default=None)
    client.set_defaults(handler=_run_client)

    return parser


def _run_simulation(args: argparse.Namespace) -> None:
    result = run_scenario(args.scenario, args.output_dir, args.settings)
    print(json.dumps(result, indent=2))


def _run_all(args: argparse.Namespace) -> None:
    summaries = [run_scenario(name, args.output_dir) for name in list_scenarios()]
    print(json.dumps(summaries, indent=2))


def _run_server(args: argparse.Namespace) -> None:
    from .opcua_gateway import run_server
    asyncio.run(run_server(args.endpoint, args.tick_seconds))


def _run_client(args: argparse.Namespace) -> None:
    from .opcua_gateway import send_command
    asyncio.run(send_command(args.endpoint, args.command, args.power_mw))


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
