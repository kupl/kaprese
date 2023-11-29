import datetime
import os
from pathlib import Path

from kaprese.core.benchmark import Benchmark
from kaprese.core.engine import Engine
from kaprese.utils.docker import (
    build_image,
    delete_image,
    image_exists,
    pull_image,
    run_commands_stream,
)
from kaprese.utils.logging import enable_filelogging, logger


class Runner:
    def __init__(
        self,
        benchmark: Benchmark,
        engine: Engine,
        output_dir: str | None = None,
        extra_args: str | list[str] = "",
    ):
        self.benchmark = benchmark
        self.engine = engine
        self.extra_args = (
            extra_args if isinstance(extra_args, str) else " ".join(extra_args)
        )

        self.output_dir = Path(
            f"{output_dir or 'kaprese-out'}/{engine.name}/{benchmark.name}"
        )
        self.uid = os.getuid()
        self.gid = os.getgid()
        self.mount_dir = Path(self.benchmark.workdir or "/") / "kaprese-out"

        if self.output_dir.exists():
            logger.warning(
                'Output directory "%s" already exists, '
                "the results may be overwritten",
                self.output_dir,
            )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._start_time = None
        self._end_time = None

    @property
    def elapsed_time(self) -> datetime.timedelta | None:
        if self._start_time is None:
            return None
        return (self._end_time or datetime.datetime.now()) - self._start_time

    @property
    def _logfile(self) -> Path:
        return self.output_dir / "kaprese.log"

    @property
    def _runner_image_tag(self) -> str:
        return f"{self.engine.image}:{self.benchmark.name}"

    def prepare(self, *, force: bool = False) -> bool:
        with enable_filelogging(self._logfile, mode="w"):
            logger.info(
                "Preparing runner(%s, %s)",
                self.engine.name,
                self.benchmark.name,
            )
            runner_image_tag = self._runner_image_tag
            if force or not image_exists(runner_image_tag):
                logger.info(
                    'Trying to pull or build engine image "%s"', self.engine.image
                )
                if pull_image(runner_image_tag):
                    logger.info('Pulled runner image "%s"', runner_image_tag)

                else:
                    logger.info('No prebuilt runner image "%s"', runner_image_tag)
                    if self.engine.location is None:
                        logger.error(
                            'Failed to pull runner image "%s": no engine location provided',
                            runner_image_tag,
                        )
                        return False

                    build_args = self._process_build_args(self.engine.build_args)
                    if build_image(
                        runner_image_tag,
                        self.engine.location,
                        build_args,
                        nocache=force,
                    ):
                        logger.info('Built runner image "%s"', runner_image_tag)
                    else:
                        logger.warning(
                            'Failed to build runner image "%s": maybe wrong location? (current=%s)',
                            runner_image_tag,
                            self.engine.location,
                        )
                        return False

            logger.info(
                "Prepared runner(%s, %s)",
                self.engine.name,
                self.benchmark.name,
            )
            return True

    def run(self, *, delete_runner: bool = False) -> bool:
        with enable_filelogging(self._logfile, mode="a"):
            self._start_time = datetime.datetime.now()
            logger.info(
                "Starting runner(%s, %s) at %s",
                self.engine.name,
                self.benchmark.name,
                self._start_time,
            )

            runner_image_tag = f"{self.engine.image}:{self.benchmark.name}"

            logger.info(
                'Running benchmark "%s" with engine "%s"',
                self.benchmark.name,
                self.engine.name,
            )

            commands = (
                [self.engine.exec_commands]
                if isinstance(self.engine.exec_commands, str)
                else self.engine.exec_commands
            )
            if isinstance(commands, list):
                commands = [self._process_command(c) for c in commands]

            with run_commands_stream(
                runner_image_tag,
                commands,
                workdir=self.benchmark.workdir,
                mount={self.output_dir: self.mount_dir},
            ) as result:
                if result.stream is not None:
                    for line in result.stream:
                        logger.debug(
                            "Runner(%s, %s) %s",
                            self.engine.name,
                            self.benchmark.name,
                            line.decode().strip("\n"),
                        )

            if delete_runner:
                logger.info('Deleting runner image "%s"', runner_image_tag)
                delete_image(runner_image_tag)

            self._end_time = datetime.datetime.now()
            logger.info(
                "Finished runner(%s, %s) at %s (elapsed time: %s)",
                self.engine.name,
                self.benchmark.name,
                self._end_time,
                self.elapsed_time,
            )
            return code == 0 if (code := result.return_code) is not None else False

    def _format(self, s: str) -> str:
        return s.format(
            benchmark=self.benchmark,
            engine=self.engine,
            runner=self,
        )

    def _process_build_args(self, build_args: dict[str, str]) -> dict[str, str]:
        return {k: self._format(v) for k, v in build_args.items()}

    def _process_command(self, command: str) -> str:
        return self._format(command)
