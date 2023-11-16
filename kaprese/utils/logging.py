import logging
import os

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
