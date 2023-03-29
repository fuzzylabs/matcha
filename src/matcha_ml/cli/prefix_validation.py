"""Validation functions for resource name prefix."""
import re
from typing import Set, Tuple

import typer
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient


def check_prefix_naming_rules(value: str) -> bool:
    """Check whether the prefix passes the azure's naming rules.

    Args:
        value (str): the prefix entered by user.

    Raises:
        BadParameter: raise when the user has provided a prefix containing non-alphanumeric characters or hyphens
        BadParameter: raise when the user has provided a prefix starts or ends with a hyphen
        BadParameter: raise when the user has provided a prefix shorter or longer than the required prefix length

    Returns:
        bool: True if prefix is valid.
    """
    alphanumeric_pattern = r"^[a-zA-Z0-9\-]*$"
    hyphen_start_end_pattern = r"^([^-].*[^-]|[^-])$"
    length_pattern = r"^[a-zA-Z0-9\-]{3,24}$"

    if not re.match(alphanumeric_pattern, value):
        raise typer.BadParameter(
            "Resource group name prefix must contain only alphanumeric characters and hyphens."
        )

    if not re.match(hyphen_start_end_pattern, value):
        raise typer.BadParameter(
            "Resource group name prefix cannot start or end with a hyphen."
        )

    if not re.match(length_pattern, value):
        raise typer.BadParameter(
            "Resource group name prefix must be between 3 and 24 characters long."
        )

    return True


def get_credential_and_subscription_id() -> Tuple[AzureCliCredential, str]:
    """Get user's azure credential and subscription id.

    Returns:
        Tuple[AzureCliCredential, str]: user's azure credential and subscription id
    """
    credential = AzureCliCredential()

    # Initialize the Subscription Management client object
    subscription_client = SubscriptionClient(credential)

    # Get default Subscription ID
    subscription_id = next(subscription_client.subscriptions.list()).subscription_id

    return credential, subscription_id


def get_existing_resource_group_names() -> Set[str]:
    """Get the names of existing resource groups.

    Returns:
        Set[str]: Set of existing resource group names.
    """
    credential, subscription_id = get_credential_and_subscription_id()

    # Initialize the ResourceManagementClient object
    resource_client = ResourceManagementClient(credential, subscription_id)

    # Get a list of all resource groups in the subscription
    resource_groups = resource_client.resource_groups.list()

    # Extract the names of the resource groups
    resource_group_names = {rg.name for rg in resource_groups}

    return resource_group_names


def validate_prefix(value: str) -> str:
    """Validate the prefix entered by users.

    Args:
        value (str): the prefix entered by user.

    Raises:
        BadParameter: raise when the user has provided an invalid prefix value.

    Returns:
        str: the valid prefix entered by user.
    """
    if check_prefix_naming_rules(value):
        existing_resource_group_names = get_existing_resource_group_names()

        if f"{value}-resources" in existing_resource_group_names:
            raise typer.BadParameter(
                "You entered a resource group name prefix that have been used before, prefix must be unique."
            )

        return value
