import argparse
import logging
from datetime import datetime
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
            # Waiting
            Literal["Pending"],
            # Doing something
            Literal["Checking"],
            Literal["Preparing"],
            Literal["Running"],
            # Done
            Literal["Not supported"],
            Literal["Failed preparing"],
            Literal["Failed running"],
            Literal["OK"],
        ] = "Pending"
        self._spinner = None

    def check_start(self) -> None:
        self._status = "Checking"
        self._spinner = Spinner("dots", "Checking...")

    def check_done(self, passed: bool) -> None:
        self._status = "Pending" if passed else "Not supported"
        self._spinner = None

    def prepare_start(self) -> None:
        self._status = "Preparing"
        self._spinner = Spinner("dots", "Preparing...")

    def prepare_done(self, done: bool) -> None:
        self._status = "Pending" if done else "Failed preparing"
        self._spinner = None

    def run_start(self) -> None:
        self._status = "Running"
        self._spinner = Spinner("dots", "Running...")

    def run_done(self, result: bool) -> None:
        self._status = "OK" if result else "Failed running"
        self._spinner = None

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        if self._status == "Pending" or self._status == "Not supported":
            yield Text(self._status, style="grey23")
        elif (
            self._status == "Running"
            or self._status == "Checking"
            or self._status == "Preparing"
        ):
            yield self._spinner.render(
                console.get_time()
            ) if self._spinner is not None else f"{self._status}..."
        elif self._status == "OK":
            yield Text(self._status, style="green")
        else:
            yield Text(self._status, style="red")

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        if (
            self._status == "Running"
            or self._status == "Checking"
            or self._status == "Preparing"
        ):
            return Measurement(len(self._status) + 5, len(self._status) + 5)
        else:
            return Measurement(len(self._status), len(self._status))


class _TextCell:
    def __init__(self) -> None:
        self.text = None

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield Text(self.text) if self.text is not None else Text("n/a", style="grey23")

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        return (
            Measurement(len(self.text), len(self.text))
            if self.text is not None
            else Measurement(3, 3)
        )

    def set_text(self, text: str) -> None:
        self.text = text


class _Timer:
    def __init__(self) -> None:
        self.start_time = None
        self.elapsed_time = None

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        elapsed = self._elapsed
        if elapsed is None:
            yield Text("n/a", style="grey23")
        else:
            yield Text(elapsed)

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        elapsed = self._elapsed
        if elapsed is None:
            return Measurement(3, 3)
        else:
            size = len(elapsed)
            return Measurement(size, size)

    def start_timer(self) -> None:
        self.start_time = datetime.now()

    def stop_timer(self) -> None:
        self.elapsed_time = (
            (datetime.now() - self.start_time) if self.start_time is not None else None
        )

    @property
    def _elapsed(self) -> str | None:
        elapsed = (
            self.elapsed_time
            if self.elapsed_time is not None
            else (
                datetime.now() - self.start_time
                if self.start_time is not None
                else None
            )
        )
        if elapsed is None:
            return None
        else:
            t, ms = str(elapsed).split(".")
            return f"{t}.{ms[:2]}"


class _SummaryRow:
    def __init__(self, engine: str, benchmark: str) -> None:
        self.engine = engine
        self.benchmark = benchmark
        self.status = _RunnerStatus()
        self.output_dir = _TextCell()
        self.elapsed_time = _Timer()

    # check

    def check_start(self):
        self.status.check_start()

    def check_done(self, passed: bool):
        self.status.check_done(passed)

    # prepare

    def prepare_start(self):
        self.status.prepare_start()

    def prepare_done(self, done: bool):
        self.status.prepare_done(done)

    # run

    def run_start(self, output_dir: str):
        self.status.run_start()
        self.output_dir.set_text(output_dir)
        self.elapsed_time.start_timer()

    def run_done(self, result: bool):
        self.status.run_done(result)
        self.elapsed_time.stop_timer()


class _SummaryTable:
    def __init__(self, title: str = "kaprese running summary") -> None:
        self._title = title
        self._rows: list[tuple[str, _SummaryRow]] = []

    def add_row(
        self,
        engine: str,
        benchmark: str,
    ) -> _SummaryRow:
        row = _SummaryRow(engine, benchmark)
        self._rows.append((str(len(self._rows) + 1), row))
        return row

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        table = Table(title="kaprese running summary")
        table.add_column("#", justify="right")
        table.add_column("Engine", justify="left")
        table.add_column("Benchmark", justify="left")
        table.add_column("Status", justify="left")
        table.add_column("Output directory", justify="left")
        table.add_column("Elapsed time", justify="left")
        for idx, row in self._rows[-(options.max_height - 5) :]:
            table.add_row(
                idx,
                row.engine,
                row.benchmark,
                row.status,
                row.output_dir,
                row.elapsed_time,
            )
        yield table

    @property
    def full_table(self) -> Table:
        table = Table(title=self._title)
        table.add_column("#", justify="right")
        table.add_column("Engine", justify="left")
        table.add_column("Benchmark", justify="left")
        table.add_column("Status", justify="left")
        table.add_column("Output directory", justify="left")
        table.add_column("Elapsed time", justify="left")
        for idx, row in self._rows:
            table.add_row(
                idx,
                row.engine,
                row.benchmark,
                row.status,
                row.output_dir,
                row.elapsed_time,
            )
        return table


def main(
    parser: argparse.ArgumentParser,
    argv: list[str],
    args: argparse.Namespace,
) -> None:
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="show this help message and exit",
    )
    parser.add_argument(
        "--delete-runner",
        action="store_true",
        help="delete runner image after running",
    )
    parser.add_argument(
        "--rebuild-runner",
        action="store_true",
        help="rebuild runner image",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="kaprese-out",
        help="output directory (default=%(default)s)",
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
            logger.warning('Engine "%s" not found', engine_name)
            console.print(f'Engine "{engine_name}" not found (ignored)')
            continue
        engines.append(engine)
    benchmarks: list[Benchmark] = []
    for bench_name in args.benchmark:
        bench = Benchmark.load(bench_name)
        if bench is None:
            logger.warning('Benchmark "%s" not found', bench_name)
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

    table = _SummaryTable(title="kaprese running summary")
    layout["summary"].update(Align.center(table, vertical="middle"))

    logger.removeHandler(logger.handlers[0])
    pannel_console = PanelConsole()
    handler = RichHandler(console=pannel_console, show_path=False)
    handler.setFormatter(logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)
    layout["log"].update(Panel(pannel_console, title="logs"))

    with Live(layout, console=console, screen=True, refresh_per_second=12.5):
        for engine, bench in product(engines, benchmarks):
            # Make row in summary table
            row = table.add_row(engine.name, bench.name)

            # Start checking
            row.check_start()
            if not bench.availability:
                logger.info('Benchmark "%s" is not available, try to prepare it', bench.name)
                bench.prepare()
            support_check = engine.support(bench)
            row.check_done(support_check)
            if not support_check:
                logger.warning(
                    'Engine "%s" does not support benchmark "%s"',
                    engine.name,
                    bench.name,
                )
                continue

            # Start preparing
            row.prepare_start()
            runner = Runner(bench, engine, args.output)
            prepared = runner.prepare(force=args.rebuild_runner)
            row.prepare_done(prepared)
            if not prepared:
                continue

            # Start running
            logger.info('Running "%s" on "%s"', bench.name, engine.name)
            row.run_start(str(runner.output_dir))

            # Actual run
            result = runner.run(delete_runner=args.delete_runner)

            # Finish running
            row.run_done(result)

        pannel_console.print(":party_popper: Done! Press Ctrl+C to exit.")
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            pass
    console.clear()
    console.print(table.full_table)
