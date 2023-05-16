"""Reusable fixtures."""
import os
import tempfile
from typing import Iterator
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from azure.mgmt.confluent.models._confluent_management_client_enums import (
    ProvisionState,  # type: ignore [import]
)
from typer.testing import CliRunner

from matcha_ml.services import AzureClient
from matcha_ml.services.global_parameters_service import GlobalParameters

INTERNAL_FUNCTION_STUB = "matcha_ml.services.AzureClient"


@pytest.fixture
def runner():
    """A fixture for cli runner."""
    return CliRunner()


@pytest.fixture
def matcha_testing_directory() -> Iterator[str]:
    """A fixture for creating and removing temporary test directory for storing and moving files.

    Yields:
        str: a path to temporary directory for storing and moving files from tests.
    """
    temp_dir = tempfile.TemporaryDirectory()

    # tests are executed at this point
    yield temp_dir.name

    # delete temp folder
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
        f"{INTERNAL_FUNCTION_STUB}._check_required_role_assignments"
    ) as roles:
        auth.return_value = True
        sub.return_value = "id"
        rg.return_value = None
        rg_state.return_value = ProvisionState.SUCCEEDED
        roles.return_value = True

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


# GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB = "matcha_ml.services.global_parameters_service.GlobalParameters"
# GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB = "matcha_ml.cli.cli.GlobalParameters"
GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB = (
    "matcha_ml.services.analytics_service.GlobalParameters"
)


@pytest.fixture(autouse=True)
def mocked_global_parameters_service(matcha_testing_directory):
    """Mocked global parameters service.

    Args:
        matcha_testing_directory (str): Temporary directory for testing.

    Yields:
        GlobalParameters: GlobalParameters object with mocked properties.
    """
    with patch(
        f"{GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB}.default_config_file_path",
        new_callable=PropertyMock,
    ) as file_path, patch(
        f"{GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB}.user_id",
        new_callable=PropertyMock,
    ) as user_id:
        file_path.return_value = str(
            os.path.join(str(matcha_testing_directory), ".matcha-ml", "config.yaml")
        )
        user_id.return_value = "TestUserID"

        yield GlobalParameters()


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
