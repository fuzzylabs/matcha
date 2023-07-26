"""UI spinner functions."""
from types import TracebackType
from typing import Optional, Type

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

SPINNER = "dots"


class Spinner:
    """Spinner from rich.

    Implements a context manager interface using the __enter__() and __exit__() methods.
    """

    status: str
    progress: Progress

    def __init__(self, status: str):
        """Initialize a spinner using Progress.

        Args:
            status (str): task description
        """
        self.status = status
        self.progress = Progress(
            SpinnerColumn(spinner_name=SPINNER),
            TimeElapsedColumn(),
            TextColumn("[progress.description]{task.description}"),
        )
        self.progress.add_task(description=status, total=None)

    def __enter__(self) -> "Spinner":
        """Call when a spinner object is created using a `with` statement.

        Returns:
            Spinner: the instance for a context manager.
        """
        self.progress.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Called when the with block is exited to stop the progress spinner."""
        self.progress.stop()
