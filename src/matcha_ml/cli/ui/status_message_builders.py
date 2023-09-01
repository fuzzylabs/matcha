"""UI status message builders."""
import time
from random import shuffle
from typing import List, Optional, Tuple

from rich.console import Console

from matcha_ml.cli.constants import (
    INFRA_FACTS,
    RESOURCE_MSG_CORE,
    RESOURCE_MSG_MODULES,
    STATE_RESOURCE_MSG,
)
from matcha_ml.cli.ui.spinner import Spinner
from matcha_ml.config.matcha_config import MatchaConfigComponent
from matcha_ml.constants import DEFAULT_STACK

err_console = Console(stderr=True)


def build_resources_msg_content(
    stack: Optional[MatchaConfigComponent] = None, destroy: Optional[bool] = False
) -> List[Tuple[str, str]]:
    """Build the resource message that is outputted to the user at provision and destroy.

    Args:
        stack (Optional[MatchaConfigComponent]): the stack to build the resource message from. Defaults to None.
        destroy (Optional[bool]): the message is different when destroying, set this flag when destroying. Defaults to False.

    Returns:
        List[Tuple[str, str]]: the resource message.
    """
    stack_properties = DEFAULT_STACK if stack is None else stack.properties

    modules = [
        RESOURCE_MSG_MODULES[stack_property.name]
        for stack_property in stack_properties
        if stack_property.name != "name"
    ]

    message = RESOURCE_MSG_CORE + modules

    return message + STATE_RESOURCE_MSG if destroy else message


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

    Use white color for formatting

    Args:
        status: status message

    Returns:
        str: formatted message
    """
    return f"[bright_white]{status}[/bright_white]"


def build_step_success_status(status: str) -> str:
    """Build step success status message.

    Use green color and bold font for formatting

    Args:
        status: status message

    Returns:
        str: formatted message
    """
    return f"[green bold]{status}[/green bold]"


def build_substep_success_status(status: str) -> str:
    """Build sub-step success status message.

    Use green color for formatting

    Args:
        status: status message

    Returns:
        str: formatted message
    """
    return f"[green]{status}[/green]"


def build_warning_status(status: str) -> str:
    """Build warning status message.

    Use yellow color for formatting

    Args:
        status: status message

    Returns:
        str: formatted message
    """
    return f"[yellow]{status}[/yellow]"


def terraform_status_update(spinner: Spinner) -> None:
    """Outputs some facts about the deployment and matcha tea while the terraform functions are running.

    Args:
        spinner: The rich spinner that the messages are printed above.
    """
    infra_facts_shuffled = list(range(len(INFRA_FACTS)))
    shuffle(infra_facts_shuffled)

    time.sleep(10)  # there should be a delay prior to spitting facts.

    while True:
        fact = INFRA_FACTS[infra_facts_shuffled.pop()]
        spinner.progress.console.print(build_status(fact))
        time.sleep(10)
