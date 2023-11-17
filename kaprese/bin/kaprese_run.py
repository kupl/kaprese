import argparse
import logging
from itertools import product
from time import sleep
from typing import Literal, Union

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
from rich.layout import Layout
from rich.live import Live
from rich.logging import RichHandler
from rich.measure import Measurement
from rich.panel import Panel
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

from kaprese.core.benchmark import Benchmark
from kaprese.core.engine import Engine
from kaprese.core.runner import Runner
from kaprese.utils.console import PanelConsole, console
from kaprese.utils.logging import DATE_FORMAT, FORMAT, logger


class _RunnerStatus:
    def __init__(self) -> None:
        self._status: Union[
            Literal["Checking"],
            Literal["Pending"],
            Literal["Running"],
            Literal["Not supported"],
            Literal["OK"],
            Literal["Failed"],
        ] = "Checking"
        self._spinner = Spinner("dots", "Checking...")

    def check(self, passed: bool) -> None:
        self._status = "Pending" if passed else "Not supported"
        self._spinner = None

    def start(self) -> None:
        self._status = "Running"
        self._spinner = Spinner("dots", "Running...")

    def done(self, result: bool) -> None:
        self._status = "OK" if result else "Failed"
        self._spinner = None

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        if self._status == "Pending":
            return Text(self._status, style="grey23")
        elif self._status == "Running" or self._status == "Checking":
            yield self._spinner.render(
                console.get_time()
            ) if self._spinner is not None else f"{self._status}..."
        elif self._status == "OK":
            yield Text(self._status, style="green")
        elif self._status == "Failed" or self._status == "Not supported":
            yield Text(self._status, style="red")

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        if self._status == "Running" or self._status == "Checking":
            return Measurement(len(self._status) + 5, len(self._status) + 5)
        else:
            return Measurement(len(self._status), len(self._status))


def main(
    parser: argparse.ArgumentParser,
    argv: list[str],
    args: argparse.Namespace,
) -> None:
    parser.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )
    parser.add_argument(
        "--delete-runner", action="store_true", help="delete runner image after running"
    )
    parser.add_argument(
        "-e",
        "--engine",
        nargs="*",
        default=[],
        help='engine to run (see "kaprese engine list")',
    )
    parser.add_argument(
        "-b",
        "--benchmark",
        nargs="*",
        default=[],
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

    if len(engines) == 0 or len(benchmarks) == 0:
        logger.warning("No engine or benchmark to run")
        return

    layout = Layout()
    layout.split(
        Layout(name="main", ratio=1),
    )
    layout["main"].split_row(
        Layout(name="summary", ratio=1),
        Layout(name="log", ratio=1),
    )

    table = Table(title="kaprese running summary")
    table.add_column("Engine", justify="left")
    table.add_column("Benchmark", justify="left")
    table.add_column("Status", justify="left")
    layout["summary"].update(Align.center(table, vertical="middle"))

    logger.removeHandler(logger.handlers[0])
    pannel_console = PanelConsole()
    handler = RichHandler(console=pannel_console, show_path=False)
    handler.setFormatter(logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)
    layout["log"].update(Panel(pannel_console, title="logs"))

    with Live(layout, console=console):
        for engine, bench in product(engines, benchmarks):
            status = _RunnerStatus()
            table.add_row(engine.name, bench.name, status)
            support_check = engine.support(bench)
            status.check(support_check)
            if not support_check:
                logger.warning(
                    'Engine "%s" does not support benchmark "%s"',
                    engine.name,
                    bench.name,
                )
                continue
            status.start()
            logger.info(f"Running {bench.name} on {engine.name}")
            runner = Runner(bench, engine)
            result = runner.run(delete_runner=args.delete_runner)
            status.done(result)
        pannel_console.print(":party_popper: Done! Press Ctrl+C to exit.")
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            pass
