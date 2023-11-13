import argparse
import sys
from typing import List, Optional

from rich.table import Table

from kaprese.config import CONFIGURE, KEYS, SETTABLE_KEYS
from kaprese.utils.console import console


def main(
    argv: Optional[List[str]] = None, *, args: Optional[argparse.Namespace] = None
) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="kaprese-config")
    subparsers = parser.add_subparsers(dest="subcommand", metavar="<command>")

    show_parser = subparsers.add_parser("show", help="show configuration")
    show_parser.add_argument("-k", "--key", type=str, nargs="*")

    set_parser = subparsers.add_parser("set", help="set configuration")
    set_parser.add_argument(
        "setup", type=str, nargs="*", metavar="<key>=<value>", help="key=value"
    )

    # Branching to pass type checking
    args = parser.parse_args(argv, namespace=args) if args else parser.parse_args(argv)

    if args.subcommand == "set":
        for setup in args.setup:
            key, value = setup.split("=")
            if key not in SETTABLE_KEYS:
                raise ValueError(f"Invalid key: {key}")
            setattr(CONFIGURE, key, value)

    elif args.subcommand == "show":
        table = Table(title="kaprese configuration")
        table.add_column("key", justify="left")
        table.add_column("value", justify="left")
        table.add_column("description", justify="left")
        for key in KEYS:
            if args.key is None or key in args.key:
                table.add_row(
                    key,
                    str(getattr(CONFIGURE, key)),
                    getattr(CONFIGURE.__class__, key).__doc__,
                )
        console.print(table)

    else:
        parser.print_help()
        sys.exit(1)
