import logging
import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from rich.logging import RichHandler

from kaprese.utils.console import console

FORMAT = "%(message)s"
DATE_FORMAT = "[%X]"

_log_level = os.environ.get("LOG_LEVEL", "WARNING").upper()

_hander = RichHandler(
    console=console,
    show_path=_log_level == "DEBUG",
)
_hander.setFormatter(logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT))

logger = logging.getLogger("kaprese")
logger.addHandler(_hander)
logger.setLevel(_log_level)


@contextmanager
def enable_filelogging(path: Path | str) -> Generator[None, None, None]:
    handler = logging.FileHandler(path, mode="w")
    handler.setFormatter(
        logging.Formatter(
            fmt=f"%(asctime)-10s %(levelname)-8s {FORMAT}", datefmt=DATE_FORMAT
        )
    )
    handler.setLevel("INFO" if _log_level != "DEBUG" else _log_level)
    logger.addHandler(handler)
    try:
        yield
    finally:
        logger.removeHandler(handler)
        handler.close()
