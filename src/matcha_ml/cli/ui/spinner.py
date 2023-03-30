"""UI spinner functions."""
from types import TracebackType
from typing import Optional, Type

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

SPINNER = "dots"


class Spinner:
    status: str
    progress: Progress

    def __init__(self, status: str):
        self.status = status
        self.progress = Progress(
            SpinnerColumn(spinner_name=SPINNER),
            TimeElapsedColumn(),
            TextColumn("[progress.description]{task.description}"),
        )
        self.progress.add_task(description=status, total=None)

    def __enter__(self) -> None:
        self.progress.start()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.progress.stop()
