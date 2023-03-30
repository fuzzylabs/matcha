"""UI primitives functions."""
from typing import List, Optional, Tuple

from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

err_console = Console(stderr=True)

SPINNER = "dots"


def build_resource_confirmation(
    header: str, resources: List[Tuple[str, str]], footer: Optional[str] = None
) -> str:
    """Build resource confirmation messages.

    Args:
        header (str): header of the confirmation message.
        resources (List[Tuple[str, str]]): a list of resource name and description pairs.
        footer (Optional[str], optional): footer of the confirmation message. Defaults to None.

    Returns:
        str: the confirmation message.
    """
    message = f"{header}:\n"
    for idx, (name, description) in enumerate(resources):
        message += f"{idx+1}. [yellow]{name}[/yellow]: {description}\n"

    if footer is not None:
        message += f"\n{footer}\n"

    return message


def print_status(status: str):
    # print a grey status message
    print(f"[white]{status}[/white]")


def print_step_success(status: str):
    # green and bold status message for step completion
    print(f"[green bold]{status}[/green bold]")


def print_substep_success(status: str):
    # green status message when substep was completed.
    print(f"[green]{status}[/green]")


def print_error_message(status: str):
    err_console.print(status, style="blink")


def show_spinner(status: str):
    # show a spinner and a status message for a long running task
    with Progress(
        SpinnerColumn(spinner_name=SPINNER),
        TimeElapsedColumn(),
    ) as progress:
        progress.add_task(description=status, total=None)
