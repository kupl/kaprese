import os
from typing import Any

from rich.console import Console as DefaultConsole
from rich.console import ConsoleOptions, RenderResult
from rich.text import Text


class PanelConsole(DefaultConsole):
    def __init__(self, *arg: Any, **kwargs: Any) -> None:
        kwargs["file"] = open(os.devnull, "w")
        kwargs["record"] = True
        super().__init__(*arg, **kwargs)
        self._logs: list[Text] = []

    def __rich_console__(
        self, console: DefaultConsole, options: ConsoleOptions
    ) -> RenderResult:
        texts = (Text(text, style or "") for text, style, _ in self._record_buffer)
        lines = [line for line in Text("").join(texts).split("\n") if line.cell_len > 0]
        for line in lines:
            line.no_wrap = True
            line.overflow = "ellipsis"
        self._record_buffer.clear()
        self._logs.extend(lines)
        yield from (self._logs[-(options.max_height) :])


console = DefaultConsole()
