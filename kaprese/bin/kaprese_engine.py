import argparse
import json
import sys

from rich.table import Table

from kaprese.core.engine import Engine, all_engines
from kaprese.engines.saver import register_saver
from kaprese.utils.console import console


def main(argv: list[str] | None = None, *, args: argparse.Namespace | None = None):
    parser = argparse.ArgumentParser(prog="kaprese engine")

    subparsers = parser.add_subparsers(dest="subcommand", metavar="<command>")

    list_parser = subparsers.add_parser("list", help="list engines")
    list_parser.add_argument(
        "-q", "--quiet", action="store_true", help="only show names of engines"
    )

    inspect_parser = subparsers.add_parser("inspect", help="inspect engine")
    inspect_parser.add_argument("engine", help="engine name")

    preset_parser = subparsers.add_parser("preset", help="preset engines")
    preset_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing engines",
    )
    preset_parser.add_argument(
        "preset", nargs="*", choices=["saver"], help="preset engine name"
    )

    # Branching to pass type checking
    args = parser.parse_args(argv, namespace=args) if args else parser.parse_args(argv)

    if args.subcommand == "list":
        if args.quiet:
            for engine in all_engines():
                print(engine.name)
        else:
            table = Table(title="kaprese engines")
            table.add_column("name", justify="left")
            table.add_column("supported languages", justify="left")
            table.add_column("supported os", justify="left")
            for engine in all_engines():
                table.add_row(
                    engine.name,
                    ", ".join(engine.supported_languages),
                    ", ".join(engine.supported_os),
                )
            console.print(table)

    elif args.subcommand == "inspect":
        engine = Engine.load(args.engine)
        if engine is None:
            console.print(f'Engine "{args.engine}" not found')
            sys.exit(1)
        console.print(json.dumps(engine.dump(), indent=4))

    elif args.subcommand == "preset":
        if len(args.preset) == 0:
            preset_parser.print_help()
            sys.exit(1)
        for preset in args.preset:
            if preset == "saver":
                register_saver(overwrite=args.overwrite)
                console.print(f'preset engine "{preset}" registered')

    else:
        parser.print_help()
        sys.exit(1)
