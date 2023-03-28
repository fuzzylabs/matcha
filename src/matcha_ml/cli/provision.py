"""Provision CLI."""
import os
from typing import Optional

import typer
from rich import print

from matcha_ml.templates.build_templates.azure_template import (
    build_template,
    build_template_configuration,
)
from matcha_ml.templates.run_template import TerraformService

# create a typer app to group all provision subcommands
app = typer.Typer()


def reuse_configuration(path: str) -> bool:
    """Check if a configuration already a use, and prompt user to override or reuse it.

    Args:
        path (str): path to the infrastructure configuration

    Returns:
        bool: decision to reuse the existing configuration
    """
    if os.path.exists(path):
        summary_message = """The following resources are already configured for provisioning:
1. [yellow] Resource group [/yellow]: A resource group
2. [yellow] Azure Kubernetes Service (AKS) [/yellow]: A kubernetes cluster
3. [yellow] Azure Storage Container [/yellow]: A storage container
"""
        print(summary_message)

        return not typer.confirm(
            "Do you want to override the configuration? Otherwise, the existing configuration will be reused"
        )
    else:
        return False


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
