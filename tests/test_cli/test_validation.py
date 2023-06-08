"""Tests for cli._validation."""

import pytest
from typer import BadParameter

from matcha_ml.cli._validation import (
    find_closest_matches,
    get_command_validation,
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


@pytest.mark.parametrize(
    "prefix, expectation", [("matcha", "matcha"), ("MATCHA", "matcha")]
)
def test_prefix_typer_callback_expected(prefix: str, expectation: str):
    """Test that the callback works as expected with valid input.

    Args:
        prefix (str): the prefix acting as user input.
        expectation (str): the expected outcome of the callback.
    """
    assert prefix_typer_callback(prefix) == expectation


@pytest.mark.parametrize(
    "prefix, error_msg, expectation",
    [
        (
            "matcha&&",
            "Resource group name prefix can only contain alphanumeric characters.",
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


def test_get_command_validation_invalid_resource_name():
    """Test whether get_command_validation function raises the expected error with the expected error message when an invalid resource name is passed."""
    mock_valid_options = ["option-1", "second-option"]

    mock_argument = "option"
    expected_output = "Error - a resource type with the name 'option' does not exist. Did you mean 'option-1'?"

    with pytest.raises(MatchaInputError) as err:
        get_command_validation(mock_argument, mock_valid_options, "resource type")

    assert str(err.value) in expected_output


def test_get_command_validation_invalid_property_name():
    """Test whether get_command_validation function raises the expected error with the expected error message when an invalid property name is passed."""
    mock_valid_options = ["option-1", "second-option"]
    mock_valid_options = ["option-1", "second-option"]

    mock_argument = "second-opt"
    expected_output = "Error - a property with the name 'second-opt' does not exist. Did you mean 'second-option'?"

    with pytest.raises(MatchaInputError) as err:
        get_command_validation(mock_argument, mock_valid_options, "property")

    assert str(err.value) in expected_output
