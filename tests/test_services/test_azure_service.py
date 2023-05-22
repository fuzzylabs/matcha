"""Tests for the Azure Service."""
from unittest.mock import MagicMock

import pytest

from matcha_ml.errors import MatchaPermissionError
from matcha_ml.services import AzureClient
from matcha_ml.services.azure_service import (
    ACCEPTED_ROLE_CONFIGURATIONS,
    ROLE_ID_MAPPING,
)


def test_is_valid_region_valid_input(mocked_azure_client: AzureClient):
    """Test that the is_valid_region function produces the correct result with valid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    mocked_azure_client.fetch_regions = MagicMock(return_value=({"ukwest", "uksouth"}))
    assert mocked_azure_client.is_valid_region("ukwest")


def test_is_valid_region_invalid_input(mocked_azure_client: AzureClient):
    """Test that the is_valid_region function produces the correct result with invalid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    mocked_azure_client.fetch_regions = MagicMock(return_value=({"ukwest", "uksouth"}))
    assert not mocked_azure_client.is_valid_region("random_region")


def test_is_valid_resource_group_valid_input(mocked_azure_client: AzureClient):
    """Test that the is_valid_resource_group function produces the correct result with valid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    mocked_azure_client.fetch_resource_group_names = MagicMock(
        return_value=({"rand-prod-resources"})
    )
    assert mocked_azure_client.is_valid_resource_group("example")


def test_is_valid_resource_group_invalid_input(mocked_azure_client: AzureClient):
    """Test that the is_valid_resource_group function produces the correct result with invalid input.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    mocked_azure_client.fetch_resource_group_names = MagicMock(
        return_value=({"rand-prod-resources"})
    )
    assert not mocked_azure_client.is_valid_resource_group("rand-prod")


def test_check_required_role_assignments_expected(mocked_azure_client: AzureClient):
    """Test that the user has the required role assignments.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    assert mocked_azure_client._check_required_role_assignments()


def test_check_required_role_assignments_incorrect_permissions(
    mocked_azure_client: AzureClient,
):
    """Test that an exception is thrown when the user does not have the correct permissions.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    # set the roles to be invalid
    mocked_azure_client._fetch_user_roles.return_value = [
        "/subscriptions/id/providers/Microsoft.Authorization/roleDefinitions/invalid_id"
    ]

    with pytest.raises(MatchaPermissionError) as err:
        mocked_azure_client._check_required_role_assignments()

    assert (
        str(err.value)
        == f"Error - Matcha detected that you do not have the appropriate role-based permissions on Azure to run this action. You need one of the following role configurations: {ACCEPTED_ROLE_CONFIGURATIONS} note: list items containing multiple roles require all of the listed roles."
    )

    # Set back correct roles such that this mocked client can be reused
    mocked_azure_client._fetch_user_roles.return_value = [
        f"/subscriptions/id/providers/Microsoft.Authorization/roleDefinitions/{ROLE_ID_MAPPING['Owner']}",
        f"/subscriptions/id/providers/Microsoft.Authorization/roleDefinitions/{ROLE_ID_MAPPING['Contributor']}",
    ]


def test_fetch_connection_string_function(mocked_azure_client):
    """Test that the fetch_connection_string function produces the correct connection string.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient
    """
    conn_str = mocked_azure_client.fetch_connection_string("testaccname", "test-rg")
    assert conn_str == "mock-conn-str"
