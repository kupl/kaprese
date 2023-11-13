import logging
import os

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger = logging.getLogger("kaprese")
logger.setLevel(os.environ.get("LOG_LEVEL", "WARNING").upper())
