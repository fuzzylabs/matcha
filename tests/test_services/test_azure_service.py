"""Tests for the Azure Service."""
from unittest.mock import patch

import pytest

from matcha_ml.services import AzureClient

INTERNAL_FUNCTION_STUB = "matcha_ml.services.AzureClient"


@pytest.fixture
def mocked_azure_client() -> AzureClient:
    """The Azure Client with mocked variables.

    Returns:
        AzureClient: the mocked AzureClient.
    """
    with (
        patch(f"{INTERNAL_FUNCTION_STUB}._authenticate", return_value=True),
        patch(f"{INTERNAL_FUNCTION_STUB}._subscription_id", return_value="id"),
        patch(
            f"{INTERNAL_FUNCTION_STUB}._resource_group_names",
            return_value={"rg_name"},
        ),
    ):
        return AzureClient()


def test_fetch_regions(mocked_azure_client):
    """Test for fetching the regions has the expected results.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    expected_num_regions = 2
    regions = mocked_azure_client.fetch_regions()

    assert len(regions) == expected_num_regions

    assert {"ukwest", "uksouth"} == regions


def test_is_valid_region_valid_input(mocked_azure_client):
    """Test that the is_valid_region function produces the correct result with valid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    assert mocked_azure_client.is_valid_region("ukwest") is True


def test_is_valid_region_invalid_input(mocked_azure_client):
    """Test that the is_valid_region function produces the correct result with invalid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    assert mocked_azure_client.is_valid_region("random_region") is False
