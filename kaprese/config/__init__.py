import json
from pathlib import Path
from typing import Optional, TypedDict

from kaprese.utils.design import Singleton


class _DOCKER_CONFIG_TYPE(TypedDict):
    DOCKER_SOCK_PATH: Optional[str]


KEYS = [
    "CONFIG_PATH",
    "DOCKER_SOCK_PATH",
]


class _Configure(metaclass=Singleton):
    # Base directory
    _config_path = Path("~").expanduser() / ".kaprese"

    @property
    def CONFIG_PATH(self) -> Path:
        """Path to kaprese config directory (default=~/.kaprese)"""
        return self._config_path

    @CONFIG_PATH.setter
    def CONFIG_PATH(self, value: Path) -> None:
        self._config_path = value
        self._reload()

    # Docker settings
    _docker_config_path = _config_path / "docker.json"
    _docker_sock_path: Optional[str] = None

    def _read_docker_config(self) -> None:
        config = _DOCKER_CONFIG_TYPE(
            DOCKER_SOCK_PATH=None,
        )
        if self._docker_config_path.exists():
            config.update(json.loads(self._docker_config_path.read_text()))
        self._docker_sock_path = config.get("DOCKER_SOCK_PATH")

    def _write_docker_config(self) -> None:
        config = _DOCKER_CONFIG_TYPE(
            DOCKER_SOCK_PATH=self._docker_sock_path,
        )
        self._docker_config_path.write_text(json.dumps(config, indent=4))

    @property
    def DOCKER_SOCK_PATH(self) -> Optional[str]:
        """Path to docker socket (default="/var/run/docker.sock")"""
        return self._docker_sock_path

    @DOCKER_SOCK_PATH.setter
    def DOCKER_SOCK_PATH(self, value: str) -> None:
        self._docker_sock_path = value
        self._write_docker_config()

    # reset config
    def _reload(self) -> None:
        # Docker settings
        self._docker_config_path = self._config_path / "docker.json"
        self._docker_sock_path = None
        self._read_docker_config()

    def __init__(self) -> None:
        self._reload()


CONFIGURE = _Configure()
