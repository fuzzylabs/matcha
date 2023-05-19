"""Tests for the Azure Service."""
from unittest.mock import MagicMock


def test_is_valid_region_valid_input(mocked_azure_client):
    """Test that the is_valid_region function produces the correct result with valid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    mocked_azure_client.fetch_regions = MagicMock(return_value=({"ukwest", "uksouth"}))
    assert mocked_azure_client.is_valid_region("ukwest")


def test_is_valid_region_invalid_input(mocked_azure_client):
    """Test that the is_valid_region function produces the correct result with invalid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    mocked_azure_client.fetch_regions = MagicMock(return_value=({"ukwest", "uksouth"}))
    assert not mocked_azure_client.is_valid_region("random_region")


def test_is_valid_resource_group_valid_input(mocked_azure_client):
    """Test that the is_valid_resource_group function produces the correct result with valid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    mocked_azure_client.fetch_resource_group_names = MagicMock(
        return_value=({"rand-prod-resources"})
    )
    assert mocked_azure_client.is_valid_resource_group("example")


def test_is_valid_resource_group_invalid_input(mocked_azure_client):
    """Test that the is_valid_resource_group function produces the correct result with invalid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    mocked_azure_client.fetch_resource_group_names = MagicMock(
        return_value=({"rand-prod-resources"})
    )
    assert not mocked_azure_client.is_valid_resource_group("rand-prod")


def test_fetch_connection_string_function(mocked_azure_client):
    """Test that the fetch_connection_string function produces the correct connection string.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    conn_str = mocked_azure_client.fetch_connection_string("testaccname", "test-rg")
    assert conn_str == "mock-conn-str"
