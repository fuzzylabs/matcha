"""Tests for cli._validation."""
from unittest.mock import patch

import pytest
from typer import BadParameter

from matcha_ml.cli._validation import (
    find_closest_matches,
    region_typer_callback,
    region_validation,
)
from matcha_ml.errors import MatchaInputError

INTERNAL_FUNCTION_STUB = "matcha_ml.services.AzureClient"


@pytest.fixture
def mocked_components_validation(mocked_azure_client):
    """A fixture for mocking components in the validation that use the Azure Client.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient fixture in conftest
    """
    with (
        patch(
            f"{INTERNAL_FUNCTION_STUB}.fetch_regions",
            return_value={"ukwest", "uksouth"},
        ),
        patch(
            "matcha_ml.cli._validation.get_azure_client",
            return_value=mocked_azure_client,
        ),
    ):
        yield


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


def test_region_validation_is_valid(mocked_components_validation):
    """Test that a valid region is correctly validated.

    Args:
        mocked_components_validation (NoneType): the mocked components fixture
    """
    assert region_validation("uksouth") == "uksouth"


def test_region_validation_invalid_but_finds_a_match(mocked_components_validation):
    """Test that a match is found when a region is invalid.

    Args:
        mocked_components_validation (NoneType): the mocked components
    """
    print(type(mocked_components_validation))
    with pytest.raises(MatchaInputError) as err:
        region_validation("ukwset")
        assert "Did you mean 'ukwset'?" in str(err)


def test_region_validation_invalid_no_match(mocked_components_validation):
    """Test that no match is found when invalid.

    Args:
        mocked_components_validation (NoneType): the mocked components
    """
    with pytest.raises(MatchaInputError) as err:
        region_validation("thereisnothingclose")
        assert str(err) == "A region named 'thereisnothingclose' does not exist."


def test_region_typer_callback_expected(mocked_components_validation):
    """Test that the input callback finds the correct region.

    Args:
        mocked_components_validation (NoneType): the mocked components
    """
    assert region_typer_callback("uksouth") == "uksouth"


def test_region_typer_callback_invalid(mocked_components_validation):
    """Test that the callback raises a BadParameter error when invalid input is given.

    Args:
        mocked_components_validation (NoneType): the mocked components
    """
    with pytest.raises(BadParameter):
        region_typer_callback("ukwset")
