"""UI status message builders."""
from typing import List, Optional, Tuple

from rich.console import Console

err_console = Console(stderr=True)


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
    message = f"\n{header}:\n\n"
    for idx, (name, description) in enumerate(resources):
        message += f"{idx+1}. [yellow]{name}[/yellow]: {description}\n"

    if footer is not None:
        message += f"\n{footer}\n"

    return message


def build_status(status: str) -> str:
    """Build information status message.

    Use white colour for formatting

    Args:
        status: status message

    Returns:
        str: formatted message
    """
    return f"[bright_white]{status}[/bright_white]"


def build_step_success_status(status: str) -> str:
    """Build step success status message.

    Use green colour and bold font for formatting

    Args:
        status: status message

    Returns:
        str: formatted message
    """
    return f"[green bold]{status}[/green bold]"


def build_substep_success_status(status: str) -> str:
    """Build sub-step success status message.

    Use green colour for formatting

    Args:
        status: status message

    Returns:
        str: formatted message
    """
    return f"[green]{status}[/green]"
