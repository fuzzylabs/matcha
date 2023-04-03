"""Validation for user inputs."""
from difflib import get_close_matches
from re import match
from typing import Optional, Union

from typer import BadParameter

from matcha_ml.errors import MatchaInputError
from matcha_ml.services import AzureClient

PREFIX_RULES = {
    "alphanumeric": {
        "pattern": r"^[a-zA-Z0-9\-]*$",
        "message": "Resource group name prefix must contain only alphanumeric characters and hyphens.",
    },
    "hyphen": {
        "pattern": r"^([^-].*[^-]|[^-])$",
        "message": "Resource group name prefix cannot start or end with a hyphen.",
    },
    "length": {
        "pattern": r"^[a-zA-Z0-9\-]{3,24}$",
        "message": "Resource group name prefix must be between 3 and 24 characters long.",
    },
}


def get_azure_client() -> AzureClient:
    """Fetch an Azure Client.

    Returns:
        AzureClient: the azure client interface.
    """
    return AzureClient()


def find_closest_matches(
    pattern: str, possibilities: Union[set[str], list[str]], number_to_find: int = 1
) -> Optional[list[str]]:
    """Find the closest matches to an input.

    Args:
        pattern (str): the user input.
        possibilities (Union[set[str], list[str]]): the search space.
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
        str: _description_
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
        if not match(checker["pattern"], prefix):
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
    try:
        _is_valid_prefix(prefix)
    except MatchaInputError as e:
        raise BadParameter(str(e))

    azure_client = get_azure_client()

    print("RESOURCES", azure_client.fetch_resource_group_names())
    if not azure_client.is_valid_resource_group(prefix):
        raise BadParameter(
            "You entered a resource group name prefix that have been used before, prefix must be unique."
        )

    return prefix
