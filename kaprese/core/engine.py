from __future__ import annotations

import dataclasses
import json
import uuid
from pathlib import Path

from kaprese.core.config import CONFIGURE
from kaprese.utils.logging import logger


def _get_engine_path() -> Path:
    return CONFIGURE.CONFIG_PATH / "engines"


@dataclasses.dataclass
class Engine:
    name: str = dataclasses.field(
        default_factory=lambda: f"kaprese-{uuid.uuid4().hex[:7]}"
    )
    supported_languages: list[str] = dataclasses.field(default_factory=list)
    supported_os: list[str] = dataclasses.field(default_factory=list)
    image: str = ""
    location: str | None = dataclasses.field(default=None, repr=False)

    def __post_init__(self) -> None:
        if len(self.image) == 0:
            self.image = f"kaprese-engine-{self.name}"

    def dump(self) -> dict[str, str | list[str]]:
        return dataclasses.asdict(self)

    def save(self, path: Path | str) -> None:
        path = Path(path)
        path.write_text(
            json.dumps(
                self.dump(),
                indent=4,
            )
        )

    @classmethod
    def load(cls, name: str) -> Engine | None:
        engine_file = _get_engine_path() / f"{name}.json"
        if not engine_file.exists():
            return None
        data = json.loads(engine_file.read_text())
        return cls(**data)

    def register(self, *, overwrite: bool = False) -> None:
        engines_dir = _get_engine_path()
        if not engines_dir.exists():
            engines_dir.mkdir(parents=True)
        engine_file = engines_dir / f"{self.name}.json"
        if engine_file.exists():
            logger.warning(f"Engine {self.name} already exists")
            if not overwrite:
                return
            logger.warning(f"Overwriting engine {self.name}")
        self.save(engine_file)


def all_engines(path: Path | None = None) -> list[Engine]:
    path = path or _get_engine_path()
    return [
        engine
        for engine_file in path.glob("*.json")
        if (engine := Engine.load(engine_file.stem)) is not None
    ]
