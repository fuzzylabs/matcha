"""Provision CLI."""
import os
from typing import Optional, Tuple

import typer

from matcha_ml.cli._validation import prefix_typer_callback, region_typer_callback
from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_status,
    build_step_success_status,
    build_warning_status,
)
from matcha_ml.runners import AzureRunner
from matcha_ml.state import RemoteStateManager
from matcha_ml.templates import AzureTemplate

# create a typer app to group all provision subcommands
app = typer.Typer()


def fill_provision_variables(
    location: str,
    prefix: str,
    password: str,
) -> Tuple[str, str, str]:
    """Prompt for the provision variables if they were not provided.

    Args:
        location (str): Azure location in which all resources will be provisioned, or empty string to fill in.
        prefix (str): Prefix used for all resources, or empty string to fill in.
        password (str): Password for ZenServer, or empty string to fill in.

    Returns:
        Tuple[str, str, str]: A tuple of location, prefix and password which were filled in
    """
    if not location:
        location = typer.prompt(
            default=None,
            text="What region should your resources be provisioned in (e.g., 'ukwest')?",
            value_proc=region_typer_callback,
        )
    if not prefix:
        prefix = typer.prompt(
            text="Your resources need a name (an alphanumerical prefix; 3-11 character limit), what should matcha call them?",
            default="matcha",
            value_proc=prefix_typer_callback,
        )
    if not password:
        password = typer.prompt(
            default=None,
            text="Set a password for your deployment server",
            confirmation_prompt=True,
            hide_input=True,
        )

    return location, prefix, password


def provision_resources(
    location: str,
    prefix: str,
    password: str,
    verbose: Optional[bool] = False,
) -> None:
    """Provision cloud resources using templates.

    Args:
        location (str): Azure location in which all resources will be provisioned.
        prefix (str): Prefix used for all resources.
        password (str): Password for ZenServer.
        verbose (bool optional): additional output is show when True. Defaults to False.

    Raises:
        typer.Exit: if approval is not given by user.
        typer.Exit: if approval for removing a stale state is not given by user.
    """
    remote_state_manager = RemoteStateManager()

    if remote_state_manager.is_state_stale():
        print_status(
            build_warning_status(
                "Matcha has detected a stale state file. This means that your local configuration is out of sync with the remote state, the resource group may have been removed."
            )
        )

        if not typer.confirm(
            "Do you want to remove the existing local config and continue?"
        ):
            raise typer.Exit()

        remote_state_manager.remove_matcha_config()
        # Re-initialise remote state manager with empty state file
        remote_state_manager = RemoteStateManager()

    # Check whether remote state storage has been provisioned
    if not remote_state_manager.is_state_provisioned():
        location, prefix, _ = fill_provision_variables(
            location=location, prefix=prefix, password="temp"
        )
        # Provision a state storage if it's not provisioned
        remote_state_manager.provision_remote_state(location, prefix)

    with remote_state_manager.use_lock(), remote_state_manager.use_remote_state():
        # create a runner for provisioning resource with Terraform service.
        template_runner = AzureRunner()

        project_directory = os.getcwd()
        destination = os.path.join(
            project_directory, ".matcha", "infrastructure", "resources"
        )
        template = os.path.join(
            os.path.dirname(__file__), os.pardir, "infrastructure", "resources"
        )

        # Create a azure template object
        azure_template = AzureTemplate()

        if not azure_template.reuse_configuration(destination):
            location, prefix, password = fill_provision_variables(
                location, prefix, password
            )

            config = azure_template.build_template_configuration(
                location=location, prefix=prefix, password=password
            )
            azure_template.build_template(config, template, destination, verbose)

        # Initializes the infrastructure provisioning process.
        if template_runner.is_approved(verb="provision"):
            # provision resources by running the template
            template_runner.provision()
            print_status(build_step_success_status("Provisioning is complete!"))

        else:
            print_status(
                build_status(
                    "You decided to cancel - if you change your mind, then run 'matcha provision' again."
                )
            )
            raise typer.Exit()
