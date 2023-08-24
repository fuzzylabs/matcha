"""Tests for core._validation."""

import pytest

from matcha_ml.core._validation import (
    LONGEST_RESOURCE_NAME,
    MAXIMUM_RESOURCE_NAME_LEN,
    _check_length,
    _is_alphanumeric,
    _is_not_digits,
    is_valid_prefix,
    stack_module_is_valid,
)
from matcha_ml.errors import MatchaInputError


def test_is_valid_prefix_expected():
    """Test that the is valid prefix functions behaves as expected with correct input."""
    assert is_valid_prefix("matcha") == "matcha"


@pytest.mark.parametrize(
    "prefix, expectation", [("mat-cha", False), ("matcha", True), ("matcha123", True)]
)
def test_is_alphanumeric(prefix: str, expectation: bool):
    """Test that the _is_alphanumeric internal function works as expected.

    Args:
        prefix (str): the test prefix.
        expectation (bool): what the expected result is.
    """
    assert _is_alphanumeric(prefix) == expectation


@pytest.mark.parametrize(
    "prefix, expectation", [("thisisareallylongprefix", False), ("matcha", True)]
)
def test_check_length(prefix: str, expectation: bool):
    """Test that the _check_length internal function works as expected.

    Args:
        prefix (str): the test prefix.
        expectation (bool): what the expected result is.
    """
    assert _check_length(prefix) == expectation


@pytest.mark.parametrize(
    "prefix, expectation", [("1234", False), ("matcha", True), ("matcha123", True)]
)
def test_is_not_digits(prefix: str, expectation: bool):
    """Test that _is_not_digits works as expected.

    Args:
        prefix (str): the test prefix.
        expectation (bool): what the expected result is.
    """
    assert _is_not_digits(prefix) == expectation


@pytest.mark.parametrize(
    "prefix, error_msg, expectation",
    [
        (
            "1234",
            "Resource group name prefix cannot contain only numbers.",
            MatchaInputError,
        ),
        (
            "matcha&&",
            "Resource group name prefix can only contain alphanumeric characters.",
            MatchaInputError,
        ),
        (
            "mat-cha",
            "Resource group name prefix can only contain alphanumeric characters.",
            MatchaInputError,
        ),
        (
            "thisisareallylongprefixmatcha",
            f"Resource group name prefix must be between 3 and {MAXIMUM_RESOURCE_NAME_LEN - len(LONGEST_RESOURCE_NAME)} characters long.",
            MatchaInputError,
        ),
    ],
)
def test_is_valid_prefix_invalid(
    prefix: str, error_msg: str, expectation: MatchaInputError
):
    """Test that the is_valid_prefix function behaves as expected when invalid input is given.

    Args:
        prefix (str): the invalid prefix.
        error_msg (str): the specific error message that is expected.
        expectation (MatchaInputError): the error that is expected to be raised.
    """
    with pytest.raises(expectation) as err:
        is_valid_prefix(prefix)

    assert str(err.value) == error_msg


def test_stack_module_is_valid_with_valid_module():
    """Test stack module validation returns True when the module is valid."""
    assert stack_module_is_valid("zenml")


def test_stack_module_is_valid_with_valid_module_with_upper_case():
    """Test stack module validation returns False when the module is fully upper case and not valid."""
    assert not stack_module_is_valid("ZENML")


def test_stack_module_is_valid_with_invalid_module():
    """Test stack module validation returns False when the module does not exist."""
    assert not stack_module_is_valid("invalidmodule")
