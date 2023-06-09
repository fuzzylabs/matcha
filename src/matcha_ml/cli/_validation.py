"""Validation for cli inputs."""
from difflib import get_close_matches
from typing import List, Optional, Set, Union

from typer import BadParameter

from matcha_ml.core._validation import is_valid_prefix, is_valid_region
from matcha_ml.errors import MatchaInputError
from matcha_ml.services import AzureClient


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
    if is_valid_region(region):
        return region
    else:
        azure_client = AzureClient()
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
        is_valid_prefix(prefix)
    except MatchaInputError as e:
        raise BadParameter(str(e))

    return prefix


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
