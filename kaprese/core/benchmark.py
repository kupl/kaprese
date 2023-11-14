from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from kaprese.core.config import CONFIGURE
from kaprese.utils.docker import image_exists, run_command
from kaprese.utils.logging import logger


def _get_benchmark_path() -> Path:
    return CONFIGURE.CONFIG_PATH / "benchmarks"


@dataclasses.dataclass
class Benchmark:
    name: str
    image: str
    _language: str | None = None
    language_command: str | None = dataclasses.field(default=None, repr=False)

    @property
    def language(self) -> str | None:
        if self._language is None and self.availability and image_exists(self.image):
            out = run_command(self.image, self.language_command)
            if out is not None:
                out = out.strip()
            self._language = out
        return self._language

    @property
    def availability(self) -> bool:
        return image_exists(self.image)

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

    def unregister(self) -> None:
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
