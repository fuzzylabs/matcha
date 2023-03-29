"""Build a template for provisioning resources on Azure using terraform files."""
import dataclasses
import glob
import json
import os
from shutil import copy, rmtree
from typing import Optional

import typer

from matcha_ml.cli.common_ui_primitives.ui_functions import (
    print_confirm_message,
    print_status,
    print_step_success,
    print_substep_success,
)
from matcha_ml.errors import MatchaPermissionError

SUBMODULE_NAMES = ["aks", "resource_group", "mlflow-module", "storage"]


@dataclasses.dataclass
class TemplateVariables:
    """Terraform template variables."""

    # Azure location in which all resources will be provisioned
    location: str

    # Prefix used for all resources
    prefix: str


def reuse_configuration(path: str) -> bool:
    """Check if a configuration already exists, and prompt user to override or reuse it.

    Args:
        path (str): path to the infrastructure configuration

    Returns:
        bool: decision to reuse the existing configuration
    """
    if os.path.exists(path):
        summary_message = """The following resources are already configured for provisioning:
1. Resource group : A resource group
2. Azure Kubernetes Service (AKS) : A kubernetes cluster
3. Azure Storage Container : A storage container
"""

        print_confirm_message(summary_message, is_list=True)

        return not typer.confirm(
            "Do you want to override the configuration? Otherwise, the existing configuration will be reused"
        )
    else:
        return False


def build_template_configuration(location: str, prefix: str) -> TemplateVariables:
    """Ask for variables and build the configuration.

    Args:
        location (str): Azure location in which all resources will be provisioned.
        prefix (str): Prefix used for all resources.

    Returns:
        TemplateVariables: Terraform variables required by a template
    """
    return TemplateVariables(location=location, prefix=prefix)


def build_template(
    config: TemplateVariables,
    template_src: str,
    destination: str = ".matcha/infrastructure",
    verbose: Optional[bool] = False,
) -> None:
    """Build and copy the template to the project directory.

    Args:
        config (TemplateVariables): variables to apply to the template
        template_src (str): path of the template to use
        destination (str): destination path to write template to. Defaults to ".matcha/infrastructure".
        verbose (bool, optional): additional output is shown when True. Defaults to False.

    Raises:
        MatchaPermissionError: when there are no write permissions on the configuration destination
    """
    try:
        print_status("Building configuration template...")

        # Override configuration if it already exists
        if os.path.exists(destination):
            rmtree(destination)

        os.makedirs(destination, exist_ok=True)
        if verbose:
            print_substep_success(
                f"Ensure template destination directory: {destination}"
            )

        # Define additional non-tf files that are needed from the main module
        main_module_filenames = [
            ".gitignore",
            ".terraform.lock.hcl",
        ]

        for filename in main_module_filenames:
            source_path = os.path.join(template_src, filename)
            destination_path = os.path.join(destination, filename)
            copy(source_path, destination_path)

        for source_path in glob.glob(os.path.join(template_src, "*.tf")):
            filename = os.path.basename(source_path)
            destination_path = os.path.join(destination, filename)
            copy(source_path, destination_path)

        for submodule_name in SUBMODULE_NAMES:
            os.makedirs(os.path.join(destination, submodule_name), exist_ok=True)
            for source_path in glob.glob(
                os.path.join(template_src, submodule_name, "*.tf")
            ):
                filename = os.path.basename(source_path)
                src_path = os.path.join(template_src, submodule_name, filename)
                destination_path = os.path.join(destination, submodule_name, filename)
                copy(src_path, destination_path)

            if verbose:
                print_substep_success(
                    f"{submodule_name} module configuration was copied"
                )

        if verbose:
            print_substep_success("Configuration was copied")

        configuration_destination = os.path.join(destination, "terraform.tfvars.json")
        with open(configuration_destination, "w") as f:
            json.dump(dataclasses.asdict(config), f)

        if verbose:
            print_substep_success("Template variables were added.")
    except PermissionError:
        raise MatchaPermissionError(path=destination)

    if verbose:
        print_step_success("Template configuration has finished!")

    print_status(f"The configuration template was written to {destination}")
