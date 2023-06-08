"""UI user approval functions."""
from typing import List, Tuple

import typer

from matcha_ml.cli.ui.emojis import Emojis
from matcha_ml.cli.ui.print_messages import (
    print_status,
)
from matcha_ml.cli.ui.status_message_builders import (
    build_resource_confirmation,
)


def is_user_approved(verb: str, resources: List[Tuple[str, str]]) -> bool:
    """Get approval from user within the CLI.

    Args:
        verb (str): the verb to use in the approval message.
        resources(list): the list of resources to be actioned by the verb to be provided to the user as a status message

    Returns:
        bool: True if user approves, False otherwise.
    """
    summary_message = build_resource_confirmation(
        header=f"The following resources will be {verb}ed",
        resources=resources,
        footer=f"{verb.capitalize()}ing the resources may take approximately 20 minutes. May we suggest you grab a cup of {Emojis.MATCHA.value}?",
    )

    print_status(summary_message)
    return typer.confirm(f"Are you happy for '{verb}' to run?")
