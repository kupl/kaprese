import argparse
import sys
from pathlib import Path
from typing import List, Optional

from kaprese import __version__
from kaprese.config import CONFIGURE


def main(argv: Optional[List[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="kaprese")
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

    subparsers = parser.add_subparsers(
        dest="subcommand", required=True, metavar="<command>"
    )
    subparsers.add_parser("config", add_help=False, help="configure kaprese")

    args, remainder = parser.parse_known_args(argv)

    if args.kaprese_config:
        CONFIGURE.CONFIG_PATH = args.kaprese_config

    if args.subcommand == "config":
        from kaprese.bin.kaprese_config import main

        main(remainder, args=args)
