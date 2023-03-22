"""Provision CLI."""
import dataclasses
import glob
import json
import os
from shutil import copy
from typing import Optional

import typer
from rich import print

# create a typer app to group all provision subcommands
app = typer.Typer()


@dataclasses.dataclass
class TemplateVariables(object):
    """Terraform template variables."""

    # Azure location in which all resources will be provisioned
    location: str

    # Prefix used for all resources
    prefix: str = "matcha"


def build_template_configuration(
    location: Optional[str] = None, prefix: Optional[str] = None
) -> TemplateVariables:
    """Ask for variables and build the configuration.

    Args:
        location (str, optional): Azure location in which all resources will be provisioned. Will be prompted for, if not provided.
        prefix (str, optional): Prefix used for all resources. Will be prompted for, if not provided.

    Returns:
        TemplateVariables: Terraform variables required by a template
    """
    if prefix is None:
        prefix = typer.prompt("Resource name prefix", type=str, default="matcha")
    if location is None:
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

    # Define additional non-tf files that are needed from the main module
    main_module_filenames = [
        ".gitignore",
        ".terraform.lock.hcl",
    ]

    submodule_names = ["aks", "resource_group"]

    print("Copying root module configuration...")
    for filename in main_module_filenames:
        source_path = os.path.join(template_src, filename)
        destination_path = os.path.join(destination, filename)
        copy(source_path, destination_path)

    for source_path in glob.glob(os.path.join(template_src, "*.tf")):
        filename = os.path.basename(source_path)
        destination_path = os.path.join(destination, filename)
        copy(source_path, destination_path)

    for submodule_name in submodule_names:
        print(f"Copying {submodule_name} module configuration...")
        os.makedirs(os.path.join(destination, submodule_name), exist_ok=True)
        for source_path in glob.glob(os.path.join(template_src, "*.tf")):
            filename = os.path.basename(source_path)
            source_path = os.path.join(template_src, submodule_name, filename)
            destination_path = os.path.join(destination, submodule_name, filename)
            copy(source_path, destination_path)
        print("[green]{submodule_name} module configuration was copied[/green]")

    print("[green]Configuration was copied[/green]")

    print("Adding template configuration...")
    configuration_destination = os.path.join(destination, "terraform.tfvars.json")
    with open(configuration_destination, "w") as f:
        json.dump(dataclasses.asdict(config), f)
    print("[green]Template configuration is added[/green]")


def provision_resources(
    location: Optional[str] = None, prefix: Optional[str] = None
) -> None:
    """Provision cloud resources with a template.

    Args:
        location (str, optional): Azure location in which all resources will be provisioned.
        prefix (str, optional): Prefix used for all resources.
    """
    project_directory = os.getcwd()
    destination = os.path.join(project_directory, ".matcha", "infrastructure")

    template = os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir, "infrastructure"
    )

    config = build_template_configuration(location, prefix)
    build_template(config, template, destination)
