"""Test suite to mock testing for AzureStorage class."""
import pytest
import os
from unittest.mock import patch

from matcha_ml.storage.azure_storage import AzureStorage

STORAGE_FUNCTION_STUB = "matcha_ml.storage.azure_storage"


@pytest.fixture
def mock_blob_service():
    """_summary_

    Yields:
        _type_: _description_
    """
    with patch(
        f"{STORAGE_FUNCTION_STUB}.BlobServiceClient.from_connection_string"
    ) as mock_blob_service:
        yield mock_blob_service


def test_upload_file(mock_blob_service, matcha_testing_directory):
    """_summary_

    Args:
        mock_blob_service (_type_): _description_
        matcha_testing_directory (_type_): _description_
    """
    test_file_path = os.path.join(matcha_testing_directory, "temp.txt")
    with open(test_file_path, "w"):
        pass

    mock_container_client = mock_blob_service.get_container_client.return_value
    mock_blob_client = mock_container_client.get_blob_client.return_value
    mock_az_storage = AzureStorage("test-storage")
    mock_az_storage.upload_file(mock_blob_client, test_file_path)

    mock_blob_client.upload_blob.assert_called_once()


# def test_upload_folder(mock_blob_service, matcha_testing_directory):
#     """_summary_

#     Args:
#         mock_blob_service (_type_): _description_
#         matcha_testing_directory (_type_): _description_
#     """
#     for i in range(1, 3):
#         tmp_file = os.path.join(matcha_testing_directory, f"temp{i}.txt")
#         with open(tmp_file, "w"):
#             pass

#     mock_container_client = mock_blob_service.get_container_client.return_value
#     mock_blob_client = mock_container_client.get_blob_client.return_value
#     mock_az_storage = AzureStorage("test-storage")
#     mock_az_storage.upload_folder(matcha_testing_directory)

#     mock_blob_client.upload_blob.assert_called()


def test_download_file(mock_blob_service, matcha_testing_directory):
    """_summary_

    Args:
        mock_blob_service (_type_): _description_
        matcha_testing_directory (_type_): _description_
    """
    test_file_path = os.path.join(matcha_testing_directory, "temp.txt")
    mock_container_client = mock_blob_service.get_container_client.return_value
    mock_blob_client = mock_container_client.get_blob_client.return_value
    mock_az_storage = AzureStorage("test-storage")
    mock_az_storage.download_file(mock_blob_client, test_file_path)

    mock_blob_client.download_blob.assert_called_once()
