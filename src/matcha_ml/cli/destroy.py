"""Destroy CLI."""
import typer

from matcha_ml.cli._validation import check_current_deployment_exists
from matcha_ml.cli.ui.print_messages import print_error, print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_status,
    build_step_success_status,
)
from matcha_ml.runners import AzureRunner
from matcha_ml.state import RemoteStateManager


def destroy_resources() -> None:
    """Destroy resources.

    Raises:
        typer.Exit: Exit if matcha remote state has not been provisioned.
        typer.Exit: if an existing deployment does not exist.
        typer.Exit: if approval is not given by user.
    """
    remote_state = RemoteStateManager()
    if not remote_state.is_state_provisioned():
        print_error(
            "Error - matcha state has not been initialized, nothing to destroy."
        )
        raise typer.Exit()

    with remote_state.use_lock():
        with remote_state.use_remote_state():
            # create a runner for deprovisioning resource with Terraform service.
            template_runner = AzureRunner()

            if not check_current_deployment_exists():
                print_error(
                    "Error - you cannot destroy resources that have not been provisioned yet."
                )
                raise typer.Exit()

            if template_runner.is_approved(verb="destroy"):
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
