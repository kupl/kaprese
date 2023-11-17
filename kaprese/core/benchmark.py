from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from kaprese.core.config import CONFIGURE
from kaprese.utils.docker import delete_image as docker_delete_image
from kaprese.utils.docker import image_exists, pull_image, run_command
from kaprese.utils.logging import logger


def _get_benchmark_path() -> Path:
    return CONFIGURE.CONFIG_PATH / "benchmarks"


@dataclasses.dataclass
class Benchmark:
    name: str
    image: str
    _language: str | None = None
    language_command: str | None = dataclasses.field(default=None, repr=False)
    _workdir: str | None = dataclasses.field(default=None, repr=False)
    workdir_command: str | None = dataclasses.field(default=None, repr=False)

    # Internal fields
    _availablility: bool = dataclasses.field(default=False, repr=False)
    _os: str | None = dataclasses.field(default=None, repr=False)

    @property
    def availability(self) -> bool:
        if not self._availablility:
            self._availablility = image_exists(self.image)
        return self._availablility

    @property
    def language(self) -> str | None:
        if self._language is None and self.availability:
            out = run_command(self.image, self.language_command)
            if out is not None:
                out = out.strip()
            self._language = out
        return self._language

    @property
    def workdir(self) -> str | None:
        if self._workdir is None and self.availability:
            out = run_command(self.image, self.workdir_command)
            if out is not None:
                out = out.strip()
            self._workdir = out
        return self._workdir

    @property
    def os(self) -> str | None:
        if self._os is None and self.availability:
            out = run_command(self.image, "cat /etc/os-release")
            if out is not None:
                out = out.strip()
                data = {
                    key.strip('"'): value.strip('"')
                    for key, value in [line.split("=") for line in out.split("\n")]
                }
                out = f'{data["ID"]}:{data["VERSION_ID"]}'
            self._os = out
        return self._os

    @property
    def ready(self) -> bool:
        return self.availability and self.language is not None

    def prepare(self, *, force: bool = False) -> Benchmark:
        if not self.availability or force:
            self.pull(force=force)
        if self.availability:
            self.language
            self.workdir
            self.os
        return self

    def pull(self, *, force: bool = False) -> Benchmark:
        if not self.availability or force:
            logger.info(f"Pulling benchmark {self.name}")
            pull_image(self.image)
        return self

    def cleanup(self, *, delete_image: bool = False) -> Benchmark:
        logger.info(f"Cleaning up benchmark {self.name}")
        if self.language_command is not None:
            self._language = None
        if self.workdir_command is not None:
            self._workdir = None
        if delete_image and self.availability:
            docker_delete_image(self.image)
        self._availablility = False
        self._os = None
        return self

    def register(self, *, overwrite: bool = False) -> None:
        benchmarks_dir = _get_benchmark_path()
        if not benchmarks_dir.exists():
            benchmarks_dir.mkdir(parents=True)
        benchmark_file = benchmarks_dir / f"{self.name}.json"
        if benchmark_file.exists():
            logger.warning(f"Benchmark {self.name} already exists")
            if not overwrite:
                return
            logger.warning("Overwriting benchmark")
        self.save(benchmark_file)

    def unregister(self, *, cleanup: bool = False) -> None:
        if cleanup:
            self.cleanup()
        benchmark_file = _get_benchmark_path() / f"{self.name}.json"
        if not benchmark_file.exists():
            logger.warning(f"Benchmark {self.name} does not exist")
            return
        benchmark_file.unlink()

    @classmethod
    def load(cls, name: str) -> Benchmark | None:
        benchmark_file = _get_benchmark_path() / f"{name}.json"
        if not benchmark_file.exists():
            logger.warning(f"Benchmark {name} does not exist")
            return None
        return cls(**json.loads(benchmark_file.read_text()))

    def save(self, path: Path | str) -> None:
        path = Path(path)
        benchmark = dataclasses.asdict(self)
        if benchmark["_language"] is None:
            del benchmark["_language"]
        del benchmark["_availablility"]
        path.write_text(json.dumps(benchmark))


def all_benchmarks(path: Path | None = None) -> list[Benchmark]:
    path = path or _get_benchmark_path()
    return (
        [
            benchmark
            for benchmark_file in path.glob("*.json")
            if (benchmark := Benchmark.load(benchmark_file.stem)) is not None
        ]
        if path.exists()
        else []
    )
