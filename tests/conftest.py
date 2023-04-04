"""Reusable fixtures."""
import tempfile
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from matcha_ml.services import AzureClient

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
    with (
        patch(f"{INTERNAL_FUNCTION_STUB}._authenticate", return_value=True),
        patch(f"{INTERNAL_FUNCTION_STUB}._subscription_id", return_value="id"),
    ):
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
