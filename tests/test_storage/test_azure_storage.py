"""Test suite to mock testing for AzureStorage class."""
import os
from unittest.mock import patch

import pytest
from azure.storage.blob import BlobProperties, BlobServiceClient

from matcha_ml.services.azure_service import AzureClient
from matcha_ml.storage.azure_storage import AzureStorage

CLASS_STUB = "matcha_ml.storage.azure_storage"


@pytest.fixture
def mock_blob_service() -> BlobServiceClient:
    """Pytest fixture for mocking a blob service client and connection string.

    Yields:
        BlobServiceClient: Mocked blob service client
    """
    with patch(
        f"{CLASS_STUB}.BlobServiceClient.from_connection_string"
    ) as mock_blob_service, patch(
        f"{CLASS_STUB}.AzureClient.fetch_connection_string"
    ) as mock_conn_str:
        mock_conn_str.return_value = "mock-conn-str"
        yield mock_blob_service


def test_upload_file(
    mock_blob_service: BlobServiceClient,
    matcha_testing_directory: str,
    mocked_azure_client: AzureClient,
):
    """Test AzureStorage upload file function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
        matcha_testing_directory (str): Temporary directory
        mocked_azure_client (AzureClient): mocked azure client
    """
    test_file_path = os.path.join(matcha_testing_directory, "temp.txt")
    with open(test_file_path, "w"):
        pass

    # Mock container client
    mock_container_client = mock_blob_service.get_container_client.return_value

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    mock_az_storage = AzureStorage("testaccount", "test-rg")
    mock_az_storage.az_client = mocked_azure_client
    mock_az_storage.upload_file(mock_blob_client, test_file_path)

    # Check if upload_blob function is called exactly once
    mock_blob_client.upload_blob.assert_called_once()


def test_upload_folder(
    mock_blob_service: BlobServiceClient,
    matcha_testing_directory: str,
    mocked_azure_client: AzureClient,
):
    """Test AzureStorage upload folder function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
        matcha_testing_directory (str): Temporary directory
        mocked_azure_client (AzureClient): mocked azure client
    """
    # Create temp files inside temp directory
    for i in range(1, 3):
        tmp_file = os.path.join(matcha_testing_directory, f"temp{i}.txt")
        with open(tmp_file, "w"):
            pass

    # Mock container client
    mock_container_client = mock_blob_service.get_container_client.return_value

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    mock_az_storage = AzureStorage("testaccount", "test-rg")
    mock_az_storage.az_client = mocked_azure_client
    # Mock _get_container_client function of AzureStorage class
    with patch.object(AzureStorage, "_get_container_client") as mock_fn:
        mock_fn.return_value = mock_container_client
        mock_az_storage.upload_folder("testcontainer", matcha_testing_directory)

        # Check if upload_blob function is called
        mock_blob_client.upload_blob.assert_called()

        # Check if upload_blob function is called exactly twice
        assert mock_blob_client.upload_blob.call_count == len(
            os.listdir(matcha_testing_directory)
        )


def test_download_file(
    mock_blob_service: BlobServiceClient,
    matcha_testing_directory: str,
    mocked_azure_client: AzureClient,
):
    """Test AzureStorage download file function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
        matcha_testing_directory (str): Temporary directory
        mocked_azure_client (AzureClient): mocked azure client
    """
    test_file_path = os.path.join(matcha_testing_directory, "temp.txt")

    # Mock container client
    mock_container_client = mock_blob_service.get_container_client.return_value

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    mock_az_storage = AzureStorage("testaccount", "test-rg")
    mock_az_storage.az_client = mocked_azure_client
    mock_az_storage.download_file(mock_blob_client, test_file_path)

    # Check if download_blob function is called exactly once
    mock_blob_client.download_blob.assert_called_once()


def test_download_folder(
    mock_blob_service: BlobServiceClient,
    matcha_testing_directory: str,
    mocked_azure_client: AzureClient,
):
    """Test AzureStorage download folder function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
        matcha_testing_directory (str): Temporary directory
        mocked_azure_client (AzureClient): mocked azure client
    """
    # Create temp files inside temp directory
    for i in range(1, 3):
        tmp_file = os.path.join(matcha_testing_directory, f"temp{i}.txt")
        with open(tmp_file, "w"):
            pass

    # Mock container client
    mock_container_client = mock_blob_service.get_container_client.return_value

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    # Mock list blobs function for container client
    mock_container_client.list_blobs.return_value = [
        BlobProperties(name=n) for n in os.listdir(matcha_testing_directory)
    ]

    mock_az_storage = AzureStorage("testaccount", "test-rg")
    mock_az_storage.az_client = mocked_azure_client
    # Mock _get_container_client function of AzureStorage class
    with patch.object(AzureStorage, "_get_container_client") as mock_fn:
        mock_fn.return_value = mock_container_client
        mock_az_storage.download_folder("testcontainer", matcha_testing_directory)

        # Check if download_blob function is called
        mock_blob_client.download_blob.assert_called()

        # Check if download_blob function is called exactly twice
        assert mock_blob_client.download_blob.call_count == len(
            os.listdir(matcha_testing_directory)
        )
