import logging
from copy import copy
import click

from typing import Literal, Optional

TRACE_LOG_LEVEL = 5

debug = False


class ColourizedFormatter(logging.Formatter):
    """
    A custom log formatter class that:
    * Outputs the LOG_LEVEL with an appropriate color.
    * If a log call includes an `extras={"color_message": ...}` it will be used
      for formatting the output, instead of the plain text message.
    """

    headers = {
        "DEBUG": click.style("DEBUG", fg="blue"),
        "INFO": click.style("INFO", fg="green"),
        "WARNING": click.style("WARNING", fg="yellow"),
        "ERROR": click.style("ERROR", fg="red"),
        "CRITICAL": click.style("CRITICAL", fg="bright_red"),
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool = False,
    ) -> None:
        self.use_colors = True
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def formatMessage(self, record: logging.LogRecord) -> str:
        if debug:
            print("")
            print(record)
            for k in dir(record):
                if k[0] != "_":
                    print(k, getattr(record, k))
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        recordcopy.levelname = self.headers.get(levelname, levelname)
        return super().formatMessage(recordcopy)
