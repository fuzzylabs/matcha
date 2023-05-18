"""Test suite to mock testing for AzureStorage class."""
import pytest
import os
from unittest.mock import patch

from matcha_ml.storage.azure_storage import AzureStorage
from azure.storage.blob import BlobProperties, BlobServiceClient

STORAGE_FUNCTION_STUB = "matcha_ml.storage.azure_storage"


@pytest.fixture
def mock_blob_service() -> BlobServiceClient:
    """_summary_

    Yields:
        BlobServiceClient: _description_
    """
    with patch(
        f"{STORAGE_FUNCTION_STUB}.BlobServiceClient.from_connection_string"
    ) as mock_blob_service:
        yield mock_blob_service


def test_upload_file(
    mock_blob_service: BlobServiceClient, matcha_testing_directory: str
):
    """Test AzureStorage upload file function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
        matcha_testing_directory (str): Temporary directory
    """
    test_file_path = os.path.join(matcha_testing_directory, "temp.txt")
    with open(test_file_path, "w"):
        pass

    mock_container_client = mock_blob_service.get_container_client.return_value
    mock_blob_client = mock_container_client.get_blob_client.return_value
    mock_az_storage = AzureStorage("test-storage")
    mock_az_storage.upload_file(mock_blob_client, test_file_path)

    mock_blob_client.upload_blob.assert_called_once()


def test_upload_folder(
    mock_blob_service: BlobServiceClient, matcha_testing_directory: str
):
    """Test AzureStorage upload folder function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
        matcha_testing_directory (str): Temporary directory
    """
    for i in range(1, 3):
        tmp_file = os.path.join(matcha_testing_directory, f"temp{i}.txt")
        with open(tmp_file, "w"):
            pass

    mock_container_client = mock_blob_service.get_container_client.return_value
    mock_blob_client = mock_container_client.get_blob_client.return_value
    mock_az_storage = AzureStorage("test-storage")
    mock_az_storage.container_client = mock_container_client
    mock_az_storage.upload_folder(matcha_testing_directory)

    mock_blob_client.upload_blob.assert_called()

    assert mock_blob_client.upload_blob.call_count == 2


def test_download_file(mock_blob_service, matcha_testing_directory):
    """Test AzureStorage download file function.

    Args:
        mock_blob_service (_type_): Mocked blob service client
        matcha_testing_directory (str): Temporary directory
    """
    test_file_path = os.path.join(matcha_testing_directory, "temp.txt")
    mock_container_client = mock_blob_service.get_container_client.return_value
    mock_blob_client = mock_container_client.get_blob_client.return_value
    mock_az_storage = AzureStorage("test-storage")
    mock_az_storage.download_file(mock_blob_client, test_file_path)

    mock_blob_client.download_blob.assert_called_once()


def test_download_folder(
    mock_blob_service: BlobServiceClient, matcha_testing_directory: str
):
    """Test AzureStorage download folder function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
        matcha_testing_directory (str): Temporary directory
    """
    for i in range(1, 3):
        tmp_file = os.path.join(matcha_testing_directory, f"temp{i}.txt")
        with open(tmp_file, "w"):
            pass

    mock_container_client = mock_blob_service.get_container_client.return_value
    mock_blob_client = mock_container_client.get_blob_client.return_value
    mock_container_client.list_blobs.return_value = [
        BlobProperties(name=n) for n in os.listdir(matcha_testing_directory)
    ]
    mock_az_storage = AzureStorage("test-storage")
    mock_az_storage.container_client = mock_container_client
    mock_az_storage.download_folder(matcha_testing_directory)

    mock_blob_client.download_blob.assert_called()

    assert mock_blob_client.download_blob.call_count == 2
