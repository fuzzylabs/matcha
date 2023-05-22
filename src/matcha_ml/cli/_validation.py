"""Validation for user inputs."""
import json
import os
from difflib import get_close_matches
from typing import List, Optional, Set, Union

from azure.mgmt.confluent.models._confluent_management_client_enums import (  # type: ignore [import]
    ProvisionState,
)
from typer import BadParameter

from matcha_ml.cli.ui.print_messages import print_error
from matcha_ml.errors import MatchaInputError
from matcha_ml.services import AzureClient

# TODO: dynamically set both of these variables
LONGEST_RESOURCE_NAME = "artifactstore"
MAXIMUM_RESOURCE_NAME_LEN = 24

MATCHA_STATE_DIR = os.path.join(".matcha", "infrastructure", "matcha.state")


def _is_alphanumeric(prefix: str) -> bool:
    """Check whether the prefix is an alphanumeric string.

    Args:
        prefix (str): the prefix to be checked.

    Returns:
        bool: True if it is an alphanumeric string; False if not.
    """
    return prefix.isalnum()


def _check_length(prefix: str) -> bool:
    """Check whether the prefix is the correct length.

    Args:
        prefix (str): the prefix to be checked.

    Returns:
        bool: True if the prefix is less than the maximum length; False if not.
    """
    return (len(prefix) + len(LONGEST_RESOURCE_NAME)) < MAXIMUM_RESOURCE_NAME_LEN


def _is_not_digits(prefix: str) -> bool:
    """Check whether the prefix is only numbers.

    Args:
        prefix (str): the prefix to be checked.

    Returns:
        bool: True if the prefix doesn't contain only numbers; False otherwise.
    """
    return not prefix.isdigit()


PREFIX_RULES = {
    "numbers": {
        "func": _is_not_digits,
        "message": "Resource group name prefix cannot contain only numbers.",
    },
    "alphanumeric": {
        "func": _is_alphanumeric,
        "message": "Resource group name prefix can only contain alphanumeric characters.",
    },
    "length": {
        "func": _check_length,
        "message": f"Resource group name prefix must be between 3 and {MAXIMUM_RESOURCE_NAME_LEN - len(LONGEST_RESOURCE_NAME)} characters long.",
    },
}


def get_azure_client() -> AzureClient:
    """Fetch an Azure Client.

    Returns:
        AzureClient: the azure client interface.
    """
    return AzureClient()


def find_closest_matches(
    pattern: str, possibilities: Union[Set[str], List[str]], number_to_find: int = 1
) -> Optional[List[str]]:
    """Find the closest matches to an input.

    Args:
        pattern (str): the user input.
        possibilities (Union[Set[str], List[str]]): the search space.
        number_to_find (int, optional): the number of matches to find. Defaults to 1.

    Returns:
        Optional[list]: a list of matches, or None if none found.
    """
    closest = get_close_matches(pattern, possibilities, n=number_to_find)

    return closest if closest else None


def region_validation(region: str) -> str:
    """Perform validation on a possible region to provision resources to.

    Args:
        region (str): the possible region.

    Raises:
        MatchaInputError: when the region isn't found but a close match is.
        MatchaInputError: when the region isn't found and there's no match

    Returns:
        str: the region if valid
    """
    azure_client = get_azure_client()

    if azure_client.is_valid_region(region):
        return region
    else:
        closest = find_closest_matches(region, azure_client.fetch_regions())

        if closest:
            raise MatchaInputError(
                f"A region named '{region}' does not exist. Did you mean '{closest[0]}'?"
            )
        else:
            raise MatchaInputError(f"A region named '{region}' does not exist.")


def region_typer_callback(region: str) -> str:
    """The typer callback for validating the user-specified region.

    Args:
        region (str): the user inputted region.

    Raises:
        BadParameter: when the region doesn't exist.

    Returns:
        str: the region after checks are passed.
    """
    if not region:
        return region

    try:
        region_validation(region)
    except MatchaInputError as e:
        raise BadParameter(str(e))

    return region


def _is_valid_prefix(prefix: str) -> str:
    """Check for whether a prefix is valid.

    Args:
        prefix (str): the prefix to check.

    Raises:
        MatchaInputError: raised when the prefix is invalid.

    Returns:
        str: if valid, the prefix is returned.
    """
    for rule, checker in PREFIX_RULES.items():
        if not checker["func"](prefix):  # type: ignore
            raise MatchaInputError(checker["message"])

    return prefix


def prefix_typer_callback(prefix: str) -> str:
    """Typer callback for the prefix - called when the user inputs a prefix.

    Args:
        prefix (str): the user inputted prefix.

    Raises:
        BadParameter: raised when the prefix doesn't pass the rules.
        BadParameter: raised when the prefix already exists.

    Returns:
        str: if valid, the prefix is returned.
    """
    if not prefix:
        return prefix

    def _to_lowercase(prefix: str) -> str:
        """Convert the prefix to lowercase (a requirement of Azure).

        Args:
            prefix (str): the prefix passed to the callback.

        Returns:
            str: the lowercase version of that prefix.
        """
        return prefix.lower()

    prefix = _to_lowercase(prefix)

    try:
        _is_valid_prefix(prefix)
    except MatchaInputError as e:
        raise BadParameter(str(e))

    azure_client = get_azure_client()

    if not azure_client.is_valid_resource_group(prefix):
        raise BadParameter(
            "You entered a resource group name prefix that have been used before, prefix must be unique."
        )

    return prefix


def check_current_deployment_exists() -> bool:
    """Checks the current deployment using the .matcha directory current contents if it exists.

    Specifically, it checks whether the resource group exists on Azure.

    Returns:
        bool: True if a deployment currently exists, else False.
    """
    if not os.path.isfile(MATCHA_STATE_DIR):
        return False

    with open(MATCHA_STATE_DIR) as f:
        data = json.load(f)

    # Check if a resource group name prefix is present in matcha.state file
    if data.get("cloud") is not None and "prefix" in data.get("cloud"):
        resource_group_name = data["cloud"]["prefix"] + "-resources"

        client = get_azure_client()
        rg_state = client.resource_group_state(resource_group_name)

        if rg_state is None:
            return False
        elif rg_state == ProvisionState.SUCCEEDED:
            return True
        else:
            print_error(
                f"Error, resource group '{resource_group_name}' is currently in the state '{rg_state.value}' which is currently not handled by matcha. Please check your resources on Azure."
            )
            return True
    else:
        return False


def get_command_validation(argument: str, valid_options: List[str], noun: str) -> None:
    """Checks if an argument exists within a list of valid options, if it is not valid an exception is raised.

    Args:
        argument (str): A string to check
        valid_options (List[str]): A list of possible valid strings
        noun (str): Either 'property' or 'resource type'

    Raises:
        MatchaInputError: Raised when the argument is not valid
    """
    if argument not in valid_options:
        err_msg = f"Error - a {noun} with the name '{argument}' does not exist."

        closest = find_closest_matches(argument, valid_options, 1)

        if closest:
            err_msg += f" Did you mean '{closest[0]}'?"

        raise MatchaInputError(err_msg)
