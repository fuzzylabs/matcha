""""Validation for core commands."""

from enum import Enum, EnumMeta

from matcha_ml.errors import MatchaInputError
from matcha_ml.services import AzureClient

# TODO: dynamically set both of these variables
LONGEST_RESOURCE_NAME = "artifactstore"
MAXIMUM_RESOURCE_NAME_LEN = 24


class StackModuleMeta(EnumMeta):
    """Metaclass for the StackModule Enum."""

    def __contains__(self, item: str) -> bool:  # type: ignore
        """Method for checking if an item is a member of the enum.

        Args:
            item (str): the quantity to check for in the Enum.

        Returns:
            True if item is a member of the Enum, False otherwise.
        """
        try:
            self(item)
        except ValueError:
            return False
        else:
            return True


class StackModule(Enum, metaclass=StackModuleMeta):
    """Enum defining valid matcha stack modules."""

    ZENML = "zenml"
    COMMON = "common"
    DVC = "dvc"
    MLFLOW = "mlflow"
    SELDON = "seldon"


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


def is_valid_prefix(prefix: str) -> str:
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

    azure_client = AzureClient()

    if not azure_client.is_valid_resource_group(prefix):
        raise MatchaInputError(
            "You entered a resource group name prefix that has been used before, the prefix must be unique."
        )

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


def stack_module_is_valid(module: str) -> bool:
    """Checks whether a module name is valid.

    Args:
        module (str): The name of the stack module.

    Returns:
        bool: True, if the module exists in the StackModule enum, otherwise, False.
    """
    return module in StackModule
