import argparse
import sys
from typing import List, Optional

from rich.table import Table

from kaprese.config import CONFIGURE, KEYS
from kaprese.utils.console import console


def main(
    argv: Optional[List[str]] = None, *, args: Optional[argparse.Namespace] = None
) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="kaprese-config")
    subparsers = parser.add_subparsers(
        dest="subcommand", required=False, metavar="<command>"
    )

    show_parser = subparsers.add_parser("show", help="show configuration")
    show_parser.add_argument("-k", "--key", type=str, nargs="*")

    # Branching to pass type checking
    args = parser.parse_args(argv, namespace=args) if args else parser.parse_args(argv)

    # kaprese config set
    if args.subcommand == "set":
        parser.add_argument("key", type=str)
        parser.add_argument("value", type=str)
        args = parser.parse_args(argv, namespace=args)
        print(args)

    # kaprese config show
    else:
        table = Table(title="kaprese configuration")
        table.add_column("key", justify="left")
        table.add_column("value", justify="left")
        table.add_column("description", justify="left")
        for key in KEYS:
            table.add_row(
                key,
                str(getattr(CONFIGURE, key)),
                getattr(CONFIGURE.__class__, key).__doc__,
            )
        console.print(table)
