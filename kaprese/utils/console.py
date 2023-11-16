import os
from typing import Any

from rich.console import Console as DefaultConsole
from rich.console import ConsoleOptions, RenderResult


class PanelConsole(DefaultConsole):
    def __init__(self, *arg: Any, **kwargs: Any) -> None:
        kwargs["file"] = open(os.devnull, "w")
        kwargs["record"] = True
        super().__init__(*arg, **kwargs)

    def __rich_console__(
        self, console: DefaultConsole, options: ConsoleOptions
    ) -> RenderResult:
        texts = self.export_text(clear=False).split("\n")
        for text in texts:
            yield text


console = DefaultConsole()
