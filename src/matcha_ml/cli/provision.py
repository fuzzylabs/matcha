"""Provision CLI."""
import os
from typing import Optional

import typer

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
