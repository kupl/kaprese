import argparse
import sys
from typing import Callable

from rich.table import Table

from kaprese.benchmarks.c import register_benchmarks as register_c_benchmarks
from kaprese.benchmarks.ocaml import register_benchmarks as register_ocaml_benchmarks
from kaprese.core.benchmark import Benchmark, all_benchmarks
from kaprese.utils.console import console
from kaprese.utils.logging import logger


def main(argv: list[str] | None = None, *, args: argparse.Namespace | None = None):
    parser = argparse.ArgumentParser(prog="kaprese benchmark")

    subparsers = parser.add_subparsers(dest="subcommand", metavar="<command>")

    list_parser = subparsers.add_parser("list", help="list benchmarks")
    list_parser.add_argument(
        "-d",
        "--detail",
        action="store_true",
        help="show details of benchmarks (this make take some time)",
    )
    list_parser.add_argument(
        "-q", "--quiet", action="store_true", help="only show names of benchmarks"
    )

    preset_parser = subparsers.add_parser("preset", help="add preset benchmarks")
    preset_parser.add_argument(
        "--overwrite", action="store_true", help="overwrite existing benchmarks"
    )
    preset_parser.add_argument(
        "preset",
        nargs="*",
        choices=["all", "ocaml", "c"],
        help="preset benchmarks to add",
    )

    prepare_parser = subparsers.add_parser("prepare", help="prepare benchmarks")
    prepare_parser.add_argument(
        "-f", "--force", action="store_true", help="force prepare benchmarks"
    )
    prepare_parser.add_argument(
        "benchmark",
        nargs="*",
        help='benchmark to prepare (see "kaprese benchmark list")',
    )

    cleanup_parser = subparsers.add_parser("cleanup", help="cleanup benchmarks")
    cleanup_parser.add_argument(
        "-d",
        "--delete-image",
        action="store_true",
        help="delete the image of benchmarks from registry",
    )
    cleanup_parser.add_argument(
        "benchmark",
        nargs="*",
        help='benchmark to cleanup (see "kaprese benchmark list")',
    )

    # Branching to pass type checking
    args = parser.parse_args(argv, namespace=args) if args else parser.parse_args(argv)

    if args.subcommand == "list":
        if args.quiet:
            for benchmark in all_benchmarks():
                print(benchmark.name)

        elif not args.detail:
            table = Table(title="kaprese benchmarks")
            table.add_column("name", justify="left")
            table.add_column("image", justify="left")
            for benchmark in all_benchmarks():
                table.add_row(benchmark.name, benchmark.image)
            console.print(table)

        else:
            table = Table(title="kaprese benchmarks")
            table.add_column("name", justify="left")
            table.add_column("image", justify="left")
            table.add_column("ready", justify="left")
            table.add_column("availability", justify="left")
            table.add_column("language", justify="left")

            with console.status("") as status:
                for i, benchmark in enumerate(all := all_benchmarks()):
                    status.update(
                        f"[bold green][{i + 1} / {len(all)}] Checking benchmark {benchmark.name}"
                    )
                    table.add_row(
                        benchmark.name,
                        benchmark.image,
                        "yes" if benchmark.ready else "[grey23]no[/grey23]",
                        "yes" if benchmark.availability else "[grey23]no[/grey23]",
                        language
                        if (language := benchmark.language)
                        else "[grey23]n/a[/grey23]",
                    )
            console.print(table)

    elif args.subcommand == "preset":
        if len(args.preset) == 0:
            preset_parser.print_help()
            sys.exit(1)
        registers: list[Callable[[bool], None]] = []
        if "ocaml" in args.preset or "all" in args.preset:
            registers.append(register_ocaml_benchmarks)
        if "c" in args.preset or "all" in args.preset:
            registers.append(register_c_benchmarks)

        for register in registers:
            register(args.overwrite)

    elif args.subcommand == "prepare":
        if len(args.benchmark) == 0:
            prepare_parser.print_help()
            sys.exit(1)

        if "all" in args.benchmark:
            args.benchmark = [b.name for b in all_benchmarks()]

        with console.status("") as status:
            for i, bench_name in enumerate(args.benchmark):
                status.update(
                    f"[bold green][{i + 1} / {len(args.benchmark)}] Preparing benchmark {bench_name}"
                )

                benchmark = Benchmark.load(bench_name)
                if benchmark is None:
                    logger.warning(f'Benchmark "{bench_name}" not found')
                    console.print(f'Benchmark "{bench_name}" not found')
                    continue

                if benchmark.ready and not args.force:
                    console.print(f'Benchmark "{bench_name}" is ready')
                    continue
                if args.force and benchmark.ready:
                    benchmark.cleanup()

                benchmark.pull(force=args.force)
                if not benchmark.availability:
                    logger.warning(f'Failed to pull benchmark "{bench_name}"')
                    console.print(f'Failed to prepare benchmark "{bench_name}"')
                    continue

                if benchmark.language is None:
                    logger.warning(
                        f'Failed to get language of benchmark "{bench_name}"'
                    )
                    console.print(f'Failed to prepare benchmark "{bench_name}"')
                    continue

                if not benchmark.ready:
                    logger.warning(f'Failed to prepare benchmark "{bench_name}"')
                    console.print(f'Failed to prepare benchmark "{bench_name}"')
                    continue

                console.print(f'Benchmark "{bench_name}" is ready')

    elif args.subcommand == "cleanup":
        if len(args.benchmark) == 0:
            cleanup_parser.print_help()
            sys.exit(1)

        if "all" in args.benchmark:
            args.benchmark = [b.name for b in all_benchmarks()]

        with console.status("") as status:
            for i, bench_name in enumerate(args.benchmark):
                status.update(
                    f"[bold green][{i + 1} / {len(args.benchmark)}] Cleaning up benchmark {bench_name}"
                )

                benchmark = Benchmark.load(bench_name)
                if benchmark is None:
                    logger.warning(f'Benchmark "{bench_name}" not found')
                    console.print(f'Benchmark "{bench_name}" not found')
                    continue

                benchmark.cleanup(delete_image=args.delete_image)
                console.print(f'Benchmark "{bench_name}" is cleaned up')

    else:
        parser.print_help()
        sys.exit(1)
