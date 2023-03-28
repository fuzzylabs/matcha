"""Build a template for provisioning resources on Azure using terraform files."""
import dataclasses
import glob
import json
import os
from shutil import copy
from typing import Optional

import typer
from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.mgmt.resource import SubscriptionClient

from matcha_ml.errors import MatchaPermissionError

SUBMODULE_NAMES = ["aks", "resource_group", "mlflow-module", "storage"]


@dataclasses.dataclass
class TemplateVariables(object):
    """Terraform template variables."""

    # Azure location in which all resources will be provisioned
    location: str

    # Prefix used for all resources
    prefix: str = "matcha"


def get_azure_locations() -> list[str]:
    """Gets a list of valid Azure location strings.

    Returns:
        list[str]: List of Azure location strings
    """
    credential = AzureCliCredential()
    subscription_client = SubscriptionClient(credential)
    sub_list = subscription_client.subscriptions.list()

    for group in list(sub_list):
        # Get all locations for a subscription
        locations = [
            location.name
            for location in subscription_client.subscriptions.list_locations(
                group.subscription_id
            )
        ]

    return locations


def verify_azure_location(location_name: str) -> bool:
    """Verifies whether the provided resource location name exists in Azure.

    Args:
        location_name (str): User inputted location.

    Returns:
        bool: Returns True if location name is valid
    """
    try:
        locations = get_azure_locations()
    except CredentialUnavailableError:
        print("Error, please run 'az login' to authenticate your account.")
        return False

    if location_name in locations:
        return True
    else:
        print(
            f"Error, location '{location_name}' does not exist. Please use one of the following Azure locations:\n{locations}."
        )
        return False


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
        prefix = typer.prompt(
            "Your resources need a name (a lowercase prefix; 3-24 character limit), what should matcha call them?",
            type=str,
            default="matcha",
        )
    if location is None:
        location = typer.prompt(
            "What region should your resources be provisioned in (e.g., 'ukwest')?",
            type=str,
        )

    if not verify_azure_location(location):
        raise typer.Exit(code=1)

    return TemplateVariables(prefix=prefix, location=location)


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
        print("Building configuration template...")

        os.makedirs(destination, exist_ok=True)
        if verbose:
            print(
                f"[green]Ensure template destination directory: {destination}[/green]"
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
                source_path = os.path.join(template_src, submodule_name, filename)
                destination_path = os.path.join(destination, submodule_name, filename)
                copy(source_path, destination_path)

            if verbose:
                print(
                    f"[green]{submodule_name} module configuration was copied[/green]"
                )

        if verbose:
            print("[green]Configuration was copied[/green]")

        configuration_destination = os.path.join(destination, "terraform.tfvars.json")
        with open(configuration_destination, "w") as f:
            json.dump(dataclasses.asdict(config), f)

        if verbose:
            print("[green]Template variables were added[/green]")
    except PermissionError:
        raise MatchaPermissionError(path=destination)

    if verbose:
        print("[green bold]Template configuration has finished![/green bold]")

    print(f"The configuration template was written to {destination}")
