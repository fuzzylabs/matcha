"""Provision CLI."""
import os
from typing import Optional

import typer
from rich import print

from matcha_ml.templates.build_templates.azure_template import (
    build_template,
    build_template_configuration,
    reuse_configuration,
)
from matcha_ml.templates.run_template import TerraformService

# create a typer app to group all provision subcommands
app = typer.Typer()


def provision_resources(
    location: Optional[str] = None,
    prefix: Optional[str] = None,
    verbose: Optional[bool] = False,
) -> None:
    """Provision cloud resources using templates.

    Args:
        location (str, optional): Azure location in which all resources will be provisioned.
        prefix (str, optional): Prefix used for all resources.
        verbose (bool optional): additional output is show when True. Defaults to False.
    """
    project_directory = os.getcwd()
    destination = os.path.join(project_directory, ".matcha", "infrastructure")

    template = os.path.join(os.path.dirname(__file__), os.pardir, "infrastructure")

    if not reuse_configuration(destination):
        config = build_template_configuration(location, prefix)
        build_template(config, template, destination, verbose)

    # create a terraform service to provision resources
    tfs = TerraformService()

    # provision resources by running the template
    tfs.provision()

    print("[green bold]Provisioning is complete![/green bold]")
