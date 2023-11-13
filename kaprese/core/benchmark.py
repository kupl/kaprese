import dataclasses
import json
from pathlib import Path

from kaprese.core.config import CONFIGURE
from kaprese.utils.logging import logger


def _get_benchmark_path() -> Path:
    return CONFIGURE.CONFIG_PATH / "benchmarks"


@dataclasses.dataclass
class Benchmark:
    name: str
    language: str
    image: str
    availability: bool

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
        benchmark_file.write_text(json.dumps(dataclasses.asdict(self)))


def all_benchmarks(path: Path | None = None) -> list[Benchmark]:
    path = path or _get_benchmark_path()
    return (
        [
            Benchmark(**json.loads(benchmark_file.read_text()))
            for benchmark_file in path.glob("*.json")
        ]
        if path.exists()
        else []
    )
