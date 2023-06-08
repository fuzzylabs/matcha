"""Destroy CLI."""
from typing import List, Tuple

import typer

from matcha_ml.cli.ui.print_messages import print_error, print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_status,
    build_step_success_status,
)
from matcha_ml.cli.ui.user_approval_functions import is_user_approved
from matcha_ml.runners import AzureRunner
from matcha_ml.state import RemoteStateManager


def destroy_resources(resources: List[Tuple[str, str]]) -> None:
    """Destroy resources.

    Args:
        resources (List[Tuple[str,str]): the list of resources to be actioned by the verb to be provided to the user as a status message

    Raises:
        typer.Exit: Exit if matcha remote state has not been provisioned.
        typer.Exit: if an existing deployment does not exist.
        typer.Exit: if approval is not given by user.
    """
    remote_state = RemoteStateManager()
    if not remote_state.is_state_provisioned():
        print_error(
            "Error - resources that have not been provisioned cannot be destroyed. Run 'matcha provision' to get started!"
        )
        raise typer.Exit()

    with remote_state.use_lock(), remote_state.use_remote_state():
        # create a runner for deprovisioning resource with Terraform service.
        template_runner = AzureRunner()

        if is_user_approved(verb="destroy", resources=resources):
            # deprovision the resources
            template_runner.deprovision()
            print_status(build_step_success_status("Destroying resources is complete!"))
        else:
            print_status(
                build_status(
                    "You decided to cancel - your resources will remain active! If you change your mind, then run 'matcha destroy' again."
                )
            )
            raise typer.Exit()
