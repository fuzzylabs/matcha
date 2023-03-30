"""UI print functions."""
import rich
from rich.console import Console

err_console = Console(stderr=True)


def print_status(status: str) -> None:
    """Print an already formatted status string.

    Args:
        status (str): formatted status string to print
    """
    rich.print(status)


def print_error(error: str) -> None:
    """Print an already formatted error string.

    Args:
        error (str): formatted error string to print
    """
    err_console.print(
        error,
        style="blink",
    )
