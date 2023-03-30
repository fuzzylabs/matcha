"""Validation functions for region name."""
import difflib
import sys
from io import StringIO
from typing import Set

import typer
from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.mgmt.resource import SubscriptionClient


def check_azure_is_authenticated() -> None:
    """Checks if Azure is authenticated.

    Raises:
        Exit: Exits CLI if Azure is not authenticated
    """
    credential = AzureCliCredential()

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


def get_azure_subscription_client() -> SubscriptionClient:
    """Gets the Azure subscriptions within a SubscriptionClient for the current user.

    Returns:
        SubscriptionClient: An object containing the subscriptions for the authenticated user.
    """
    credential = AzureCliCredential()
    subscription_client = SubscriptionClient(credential)

    return subscription_client


def get_azure_locations(subscription_client: SubscriptionClient) -> Set[str]:
    """Gets a list of valid Azure location strings.

    Args:
        subscription_client (SubscriptionClient): An object containing the subscriptions for the authenticated user

    Returns:
        Set[str]: Set of Azure location strings
    """
    sub_list = subscription_client.subscriptions.list()

    for group in list(sub_list):
        # Get all locations for a subscription
        locations = {
            location.name
            for location in subscription_client.subscriptions.list_locations(
                group.subscription_id
            )
        }

    return locations


def verify_azure_location(location_name: str) -> str:
    """Verifies whether the provided resource location name exists in Azure.

    Args:
        location_name (str): User inputted location.

    Returns:
        str: Valid location name
    """
    check_azure_is_authenticated()
    subscription_client = get_azure_subscription_client()
    locations = get_azure_locations(subscription_client)

    is_valid = location_name in locations

    if is_valid:
        return location_name
    else:
        closest_match = difflib.get_close_matches(location_name, locations, n=1)
        if closest_match:
            raise typer.BadParameter(
                f"A region named '{location_name}' does not exist.\nDid you mean '{closest_match[0]}'?"
            )
        else:
            raise typer.BadParameter(
                f"A region named '{location_name}' does not exist."
            )
