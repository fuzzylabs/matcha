""""Validation for core commands."""
import os

from matcha_ml.errors import MatchaInputError
from matcha_ml.services import AzureClient

# TODO: dynamically set both of these variables
LONGEST_RESOURCE_NAME = "artifactstore"
MAXIMUM_RESOURCE_NAME_LEN = 24
MATCHA_STATE_PATH = os.path.join(".matcha", "infrastructure", "matcha.state")


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


def is_valid_region(region: str) -> bool:
    """Perform validation on a possible region to provision resources to.

    Args:
        region (str): the possible region.

    Raises:
        MatchaInputError: when the region isn't found

    Returns:
        bool: True, if the region is valid
    """
    azure_client = AzureClient()
    return bool(azure_client.is_valid_region(region))
