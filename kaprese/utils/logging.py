import logging
import os

from rich.logging import RichHandler

from kaprese.utils.console import console

FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(console=console)],
)

logger = logging.getLogger("kaprese")
logger.setLevel(os.environ.get("LOG_LEVEL", "WARNING").upper())
