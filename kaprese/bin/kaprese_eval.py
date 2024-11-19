import argparse
import json
import sys

from rich.table import Table

from kaprese.core.engine import Engine, all_engines
from kaprese.eval import ENGINES
from kaprese.utils.console import console


def main(
    parser: argparse.ArgumentParser,
    argv: list[str],
    args: argparse.Namespace,
) -> None:
    parser.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )

    # subparsers = parser.add_subparsers(dest="subcommand", metavar="<command>")

    eval_choices = list(ENGINES.keys())

    parser.add_argument(
        "-e",
        "--engine",
        nargs="*",
        choices=eval_choices,
        help='engine to eval (see "kaprese engine list")',
    )

    # Branching to pass type checking
    args = parser.parse_args(argv, namespace=args) if args else parser.parse_args(argv)

    if args.subcommand == "eval":
        if not args.engine:
            parser.print_help()
            sys.exit(1)
        for eval in args.engine:
            engine_eval = ENGINES[eval]
            eval_result = engine_eval()

            table = Table(title=f"Eval {eval}")
            table.add_column("Total", justify="right")
            table.add_column("Correct", justify="right")
            table.add_column("Accuracy", justify="right")

            table.add_row(
                str(eval_result.get_total_count),
                str(eval_result.get_correct_count),
                f"{eval_result.accuracy:.2f}%",
            )

        console.print(table)

    else:
        parser.print_help()
        sys.exit(1)
