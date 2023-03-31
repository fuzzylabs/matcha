"""Reusable fixtures."""
import tempfile
from typing import Iterator
from unittest.mock import patch

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


@pytest.fixture(scope="session", autouse=True)
def mocked_azure_client() -> AzureClient:
    """The Azure Client with mocked variables.

    Returns:
        AzureClient: the mocked AzureClient.
    """
    with (
        patch(f"{INTERNAL_FUNCTION_STUB}._authenticate", return_value=True),
        patch(f"{INTERNAL_FUNCTION_STUB}._subscription_id", return_value="id"),
    ):
        return AzureClient()
