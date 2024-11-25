import argparse
import sys
from pathlib import Path
from typing import List, Optional

from kaprese import __version__
from kaprese.core.config import CONFIGURE


def main(argv: Optional[List[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--kaprese-config",
        type=Path,
        default=None,
        metavar="<dir>",
        help="path to kaprese config directory (default=~/.kaprese)",
    )

    subparsers = parser.add_subparsers(dest="subcommand", metavar="<command>")
    config_parser = subparsers.add_parser(
        "config",
        add_help=False,
        help="configure kaprese",
    )
    benchmark_parser = subparsers.add_parser(
        "benchmark",
        add_help=False,
        help="benchmark related commands",
    )
    subparsers.add_parser("benchmarks", add_help=False, help="list benchmarks")
    engine_parser = subparsers.add_parser(
        "engine",
        add_help=False,
        help="engine related commands",
    )
    subparsers.add_parser("engines", add_help=False, help="list engines")
    run_parser = subparsers.add_parser(
        "run",
        add_help=False,
        help="run engines on benchmarks",
    )

    subparsers.add_parser("evals", add_help=False, help="eval engines")
    eval_parser = subparsers.add_parser(
        "eval",
        add_help=False,
        help="eval engines",
    )

    args, remainder = parser.parse_known_args(argv)

    if args.kaprese_config:
        CONFIGURE.CONFIG_PATH = args.kaprese_config

    if args.subcommand == "config":
        from kaprese.bin.kaprese_config import main

        main(config_parser, remainder, args=args)

    elif args.subcommand == "benchmark":
        from kaprese.bin.kaprese_benchmark import main

        main(benchmark_parser, remainder, args=args)

    elif args.subcommand == "benchmarks":
        from kaprese.bin.kaprese_benchmark import main

        main(benchmark_parser, ["list"] + remainder, args=args)

    elif args.subcommand == "engine":
        from kaprese.bin.kaprese_engine import main

        main(engine_parser, remainder, args=args)

    elif args.subcommand == "engines":
        from kaprese.bin.kaprese_engine import main

        main(engine_parser, ["list"] + remainder, args=args)

    elif args.subcommand == "run":
        from kaprese.bin.kaprese_run import main

        main(run_parser, remainder, args)

    elif args.subcommand == "eval":
        from kaprese.bin.kaprese_eval import main

        main(eval_parser, remainder, args)

    else:
        parser.print_help()
        sys.exit(1)
