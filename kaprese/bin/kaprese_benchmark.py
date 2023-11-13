import argparse
import sys

from rich.table import Table

from kaprese.core.benchmark import all_benchmarks
from kaprese.utils.console import console


def main(argv: list[str] | None = None, *, args: argparse.Namespace | None = None):
    parser = argparse.ArgumentParser(prog="kaprese benchmark")

    subparsers = parser.add_subparsers(dest="subcommand", metavar="<command>")

    list_parser = subparsers.add_parser("list", help="list benchmarks")
    list_parser.add_argument(
        "-a", "--all", action="store_true", help="list all benchmarks"
    )

    # Branching to pass type checking
    args = parser.parse_args(argv, namespace=args) if args else parser.parse_args(argv)

    if args.subcommand == "list":
        table = Table(title="kaprese benchmarks")

        table.add_column("name", justify="left")
        table.add_column("language", justify="left")
        table.add_column("image", justify="left")
        table.add_column("avalability", justify="left")

        for benchmark in all_benchmarks():
            if not args.all and not benchmark.availability:
                continue
            table.add_row(
                benchmark.name,
                benchmark.language,
                benchmark.image,
                "yes" if benchmark.availability else "no",
            )

        console.print(table)

    else:
        parser.print_help()
        sys.exit(1)
