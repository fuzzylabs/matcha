"""Reusable fixtures."""
import os
import tempfile
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest
from azure.mgmt.confluent.models._confluent_management_client_enums import (
    ProvisionState,  # type: ignore [import]
)
from typer.testing import CliRunner

from matcha_ml.services import AzureClient
from matcha_ml.services.azure_service import ROLE_ID_MAPPING

INTERNAL_FUNCTION_STUB = "matcha_ml.services.AzureClient"


@pytest.fixture
def runner() -> CliRunner:
    """A fixture for cli runner."""
    return CliRunner()


@pytest.fixture
def matcha_testing_directory() -> Iterator[str]:
    """A fixture for creating and removing temporary test directory for storing and moving files.

    Yields:
        str: a path to temporary directory for storing and moving files from tests.
    """
    temp_dir = tempfile.TemporaryDirectory()
    original_working_directory = (
        os.getcwd()
    )  # save in case a test changes to temp directory which will be deleted

    # tests are executed at this point
    yield temp_dir.name

    # delete temp folder
    os.chdir(original_working_directory)  # restore original working directory
    temp_dir.cleanup()


@pytest.fixture(scope="session")
def mocked_azure_client() -> AzureClient:
    """The Azure Client with mocked variables.

    Returns:
        AzureClient: the mocked AzureClient.
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}._check_authentication") as auth, patch(
        f"{INTERNAL_FUNCTION_STUB}._subscription_id"
    ) as sub, patch(f"{INTERNAL_FUNCTION_STUB}.fetch_resource_groups") as rg, patch(
        f"{INTERNAL_FUNCTION_STUB}.resource_group_state"
    ) as rg_state, patch(
        f"{INTERNAL_FUNCTION_STUB}._fetch_user_roles"
    ) as roles, patch(
        f"{INTERNAL_FUNCTION_STUB}.fetch_storage_access_key"
    ) as key:
        auth.return_value = True
        sub.return_value = "id"
        rg.return_value = None
        rg_state.return_value = ProvisionState.SUCCEEDED
        roles.return_value = [
            f"/subscriptions/id/providers/Microsoft.Authorization/roleDefinitions/{ROLE_ID_MAPPING['Owner']}",
            f"/subscriptions/id/providers/Microsoft.Authorization/roleDefinitions/{ROLE_ID_MAPPING['Contributor']}",
        ]
        key.return_value = "key"

        yield AzureClient()


@pytest.fixture(scope="class", autouse=True)
def mocked_azure_client_components(mocked_azure_client):
    """A fixture for mocking components in the validation that use the Azure Client.

    Args:
        mocked_azure_client (AzureClient): the mocked AzureClient fixture in conftest
    """
    with patch("matcha_ml.cli._validation.get_azure_client") as mock:
        mock.return_value = mocked_azure_client
        mock.return_value.fetch_regions = MagicMock(
            return_value=({"uksouth", "ukwest"})
        )
        mock.return_value.fetch_resource_group_names = MagicMock(
            return_value=({"rand-resources"})
        )
        yield mock


@pytest.fixture(autouse=True)
def mocked_segment_track_decorator():
    """Mock for Segment track.

    Yields:
        MagicMock: Mocked segment track function.
    """
    with patch(
        "matcha_ml.services.analytics_service.analytics.track"
    ) as track_analytics:
        track_analytics.return_value = None

        yield track_analytics
