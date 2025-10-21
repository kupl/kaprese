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
    language_command: str | None = dataclasses.field(default=None, repr=False)
    workdir_command: str | None = dataclasses.field(default=None, repr=False)

    # Internal fields, you may set them manually rather than providing commands
    _availability: bool = dataclasses.field(default=False, repr=False, init=False)
    _language: str | None = None
    _os: str | None = dataclasses.field(default=None, repr=False)
    _workdir: str | None = dataclasses.field(default=None, repr=False)

    @property
    def availability(self) -> bool:
        availability = image_exists(self.image)
        if not availability:
            self.cleanup()
            self.register(overwrite=True)
        self._availability = availability
        return self._availability

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
                out = f"{data['ID']}:{data['VERSION_ID']}"
            self._os = out
        return self._os

    def prepare(self, *, force: bool = False) -> None:
        if not self.availability or force:
            self.pull(force=force)
        if self.availability:
            self.language
            self.workdir
            self.os

    def pull(self, *, force: bool = False) -> None:
        if not self.availability or force:
            pull_image(self.image)

    def cleanup(self, *, delete_image: bool = False) -> None:
        logger.debug(f'Cleaning up benchmark "{self.name}"')
        if self.language_command is not None:
            self._language = None
        if self.workdir_command is not None:
            self._workdir = None
        if delete_image and self.availability:
            docker_delete_image(self.image)
        self._availability = False
        self._os = None

    @property
    def _file(self) -> Path:
        return _get_benchmark_path() / f"{self.name}.json"

    def register(self, *, overwrite: bool = False) -> None:
        if self._file.exists() and not overwrite:
            logger.error(f"Benchmark {self.name} already exists")
            return
        self._create_file()

    def _create_file(self) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.touch(exist_ok=True)
        self.save()

    def unregister(self, *, delete_image: bool = False) -> None:
        self.cleanup(delete_image=delete_image)
        self._delete_file()

    def _delete_file(self) -> None:
        benchmark_file = self._file
        if not benchmark_file.exists():
            logger.error(f'Benchmark "{self.name}" does not exist')
            return
        benchmark_file.unlink()

    @classmethod
    def load(cls, name: str) -> Benchmark | None:
        benchmark_file = _get_benchmark_path() / f"{name}.json"
        if not benchmark_file.exists():
            return None
        return cls(**json.loads(benchmark_file.read_text()))

    def save(self) -> None:
        benchmark_json = self._file
        if not benchmark_json.exists():
            logger.error(f'Benchmark "{self.name}" does not exist')
            return
        benchmark = dataclasses.asdict(self)
        del benchmark["_availability"]
        benchmark_json.write_text(json.dumps(benchmark))


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
