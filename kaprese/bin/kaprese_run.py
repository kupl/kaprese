import argparse
from itertools import product

from kaprese.core.benchmark import Benchmark
from kaprese.core.engine import Engine
from kaprese.core.runner import Runner
from kaprese.utils.console import console
from kaprese.utils.logging import logger


def main(
    parser: argparse.ArgumentParser,
    argv: list[str],
    args: argparse.Namespace,
) -> None:
    parser.add_argument(
        "-e",
        "--engine",
        nargs="*",
        help='engine to run (see "kaprese engine list")',
    )
    parser.add_argument(
        "-b",
        "--benchmark",
        nargs="*",
        help='benchmark to run (see "kaprese benchmark list")',
    )

    # Branching to pass type checking
    args = parser.parse_args(argv, namespace=args) if args else parser.parse_args(argv)

    engines: list[Engine] = []
    for engine_name in args.engine:
        engine = Engine.load(engine_name)
        if engine is None:
            logger.warning(f'Engine "{engine_name}" not found')
            console.print(f'Engine "{engine_name}" not found (ignored)')
            continue
        engines.append(engine)
    benchmarks: list[Benchmark] = []
    for bench_name in args.benchmark:
        bench = Benchmark.load(bench_name)
        if bench is None:
            logger.warning(f'Benchmark "{bench_name}" not found')
            console.print(f'Benchmark "{bench_name}" not found (ignored)')
            continue
        benchmarks.append(bench)
    for engine, bench in product(engines, benchmarks):
        runner = Runner(bench, engine)
        runner.run()
