"""Tests for cli._validation."""
from unittest.mock import patch, MagicMock

import pytest
from typer import BadParameter

from matcha_ml.cli._validation import (
    _is_valid_prefix,
    find_closest_matches,
    prefix_typer_callback,
    region_typer_callback,
    region_validation,
)
from matcha_ml.errors import MatchaInputError

def test_find_closest_matches_expected():
    """Test that a closest pattern is found."""
    pattern = "world"
    possibilities = ["hello", "world"]
    number_to_find = 1

    assert (
        pattern
        == find_closest_matches(pattern, possibilities, number_to_find=number_to_find)[
            0
        ]
    )


def test_find_closest_matches_no_matches():
    """Test that None is returned when a close pattern can't be found."""
    pattern = "not here"
    possibilities = ["hello", "world"]
    number_to_find = 1

    assert (
        find_closest_matches(pattern, possibilities, number_to_find=number_to_find)
        is None
    )


def test_region_validation_is_valid():
    """Test that a valid region is correctly validated."""
    assert region_validation("uksouth") == "uksouth"


def test_region_validation_invalid_but_finds_a_match():
    """Test that a match is found when a region is invalid."""
    with pytest.raises(MatchaInputError) as err:
        region_validation("ukwset")

    assert "Did you mean 'ukwest'?" in str(err.value)


def test_region_validation_invalid_no_match():
    """Test that no match is found when invalid."""
    with pytest.raises(MatchaInputError) as err:
        region_validation("thereisnothingclose")

    assert str(err.value) == "A region named 'thereisnothingclose' does not exist."


def test_region_typer_callback_expected():
    """Test that the input callback finds the correct region."""
    assert region_typer_callback("uksouth") == "uksouth"


def test_region_typer_callback_invalid():
    """Test that the callback raises a BadParameter error when invalid input is given."""
    with pytest.raises(BadParameter):
        region_typer_callback("ukwset")


def test_is_valid_prefix_expected():
    """Test that the is valid prefix functions behaves as expected with correct input."""
    assert _is_valid_prefix("matcha") == "matcha"


@pytest.mark.parametrize(
    "prefix, error_msg, expectation",
    [
        (
            "matcha&&",
            "Resource group name prefix must contain only alphanumeric characters and hyphens.",
            MatchaInputError,
        ),
        (
            "-matcha-",
            "Resource group name prefix cannot start or end with a hyphen.",
            MatchaInputError,
        ),
        (
            "ma",
            "Resource group name prefix must be between 3 and 24 characters long.",
            MatchaInputError,
        ),
        (
            "thisisareallylongprefixmatcha",
            "Resource group name prefix must be between 3 and 24 characters long.",
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
        _is_valid_prefix(prefix)

    assert str(err.value) == error_msg


def test_prefix_typer_callback_expected():
    """Test that the callback works as expected with valid input."""
    assert prefix_typer_callback("matcha") == "matcha"


@pytest.mark.parametrize(
    "prefix, error_msg, expectation",
    [
        (
            "matcha&&",
            "Resource group name prefix must contain only alphanumeric characters and hyphens.",
            BadParameter,
        ),
        (
            "rand",
            "You entered a resource group name prefix that have been used before, prefix must be unique.",
            BadParameter,
        ),
    ],
)
def test_prefix_typer_callback_invalid(
    prefix: str, error_msg: str, expectation: BadParameter
):
    """Test that the prefix type callback behaves as expected with invalid input.

    Args:
        prefix (str): the invalid prefix.
        error_msg (str): the specific error message that is expected.
        expectation (BadParameter): the error that is expected to be raised.
    """
    with pytest.raises(expectation) as err:
        prefix_typer_callback(prefix)

    assert str(err.value) == error_msg
