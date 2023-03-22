"""Provision CLI."""
import dataclasses
import os
from typing import Optional

import typer
from rich import print

# create a typer app to group all provision subcommands
app = typer.Typer()


@dataclasses.dataclass
class TemplateVariables(object):
    """Terraform template variables."""

    # The Azure Region in which all resources should be provisioned
    location: str

    # A prefix used for all resources
    prefix: str = "matcha"


def build_template_configuration() -> TemplateVariables:
    """Ask for variables and build the configuration.

    Returns:
        TemplateVariables: Terraform variables required by a template
    """
    prefix = typer.prompt("Resource name prefix", type=str, default="matcha")
    location = typer.prompt("Resource location", type=str)

    return TemplateVariables(prefix=prefix, location=location)


def build_template(
    config: TemplateVariables,
    template_src: str,
    destination: str = ".matcha/infrastructure",
) -> None:
    """Build and copy the template to the project directory.

    Args:
        config (TemplateVariables): variables to apply to the template
        template_src (str): path of the template to use
        destination (str): destination path to write template to
    """
    print("Building infrastructure template...")
    os.makedirs(destination, exist_ok=True)
    print(f"[green]Ensure template destination directory: {destination}[/green]")
    # TODO test how error for directory cannot be created is handled?

    # TODO copy template to destination
    # TODO write template variables to destination


@app.command()
def provision(
    template: Optional[str] = typer.Option(
        None, help="Template to use for provisioning."
    )
) -> None:
    """Provision cloud resources with a template.

    Args:
        template (str, optional): Path to template.
                                Defaults to typer.Option(..., help="Template to use for provisioning.").
    """
    project_directory = os.getcwd()
    destination = os.path.join(project_directory, ".matcha", "infrastructure")
    config = build_template_configuration()
    build_template(config, "", destination)
