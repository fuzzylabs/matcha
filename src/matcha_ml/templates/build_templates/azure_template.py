"""Build a template for provisioning resources on Azure using terraform files."""
import dataclasses
import difflib
import glob
import json
import os
import sys
from io import StringIO
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


def authenticate_azure() -> SubscriptionClient:
    """Checks Azure authentication and gets the Azure subscriptions within a SubscriptionClient for the current user.

    Returns:
        SubscriptionClient: An object containing the subscriptions for the authenticated user.
    """
    credential = AzureCliCredential()
    subscription_client = SubscriptionClient(credential)

    output = StringIO()
    # redirect stdout and stderr to the StringIO object
    sys.stdout = output
    sys.stderr = output

    try:
        # Check authentication
        credential.get_token("https://management.azure.com/.default")
    except CredentialUnavailableError:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        print(
            "Error, Matcha couldn't authenticate you with Azure! Make sure to run 'az login' before trying to provision resources."
        )
        raise typer.Exit(code=1)

    # restore stdout and stderr to their original values
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    return subscription_client


def get_azure_locations(subscription_client: SubscriptionClient) -> set[str]:
    """Gets a list of valid Azure location strings.

    Args:
        subscription_client (SubscriptionClient): An object containing the subscriptions for the authenticated user

    Returns:
        set[str]: Set of Azure location strings
    """
    sub_list = subscription_client.subscriptions.list()

    for group in list(sub_list):
        # Get all locations for a subscription
        locations = set(
            [
                location.name
                for location in subscription_client.subscriptions.list_locations(
                    group.subscription_id
                )
            ]
        )

    return locations


def verify_azure_location(location_name: str) -> tuple[bool, str]:
    """Verifies whether the provided resource location name exists in Azure.

    Args:
        location_name (str): User inputted location.

    Returns:
        bool: Returns True if location name is valid
        str: Closest valid location name
    """
    subscription_client = authenticate_azure()
    locations = get_azure_locations(subscription_client)

    closest_match = difflib.get_close_matches(location_name, locations, n=1)

    if not closest_match:
        return location_name in locations, ""
    else:
        return location_name in locations, closest_match[0]


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

    while True:
        is_valid, closest_match = verify_azure_location(location)
        if is_valid:
            break
        else:
            if closest_match:
                print(f"Did you mean '{closest_match}'?")
            print(
                f"Error, region '{location}' does not exist. See https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies for all available regions."
            )

        location = typer.prompt(
            "What region should your resources be provisioned in (e.g., 'ukwest')?",
            type=str,
        )

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
