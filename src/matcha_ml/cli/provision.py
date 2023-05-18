"""Provision CLI."""
import os
from typing import Optional, Tuple

import typer

from matcha_ml.cli._validation import prefix_typer_callback, region_typer_callback
from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_status,
    build_step_success_status,
)
from matcha_ml.templates.build_templates.azure_template import (
    build_template,
    build_template_configuration,
    reuse_configuration,
)
from matcha_ml.templates.run_template import TemplateRunner

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
    """
    # create a runner for provisioning resource with Terraform service.
    template_runner = TemplateRunner()

    project_directory = os.getcwd()
    destination = os.path.join(project_directory, ".matcha", "infrastructure")
    template = os.path.join(os.path.dirname(__file__), os.pardir, "infrastructure")

    if not reuse_configuration(destination):
        location, prefix, password = fill_provision_variables(
            location, prefix, password
        )
        config = build_template_configuration(location, prefix, password)
        build_template(config, template, destination, verbose)

    # initialises the infrastructure provisioning process.
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
