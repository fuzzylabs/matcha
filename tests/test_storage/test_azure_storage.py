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
    ) as mock_conn_str, patch(
        f"{CLASS_STUB}.AzureClient.resource_group_exists"
    ) as rg_exists:
        mock_conn_str.return_value = "mock-conn-str"
        rg_exists.return_value = True
        yield mock_blob_service


def test_container_exists(
    mock_blob_service: BlobServiceClient, mocked_azure_client: AzureClient
):
    """Test that the method returns True when a container exists.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
        mocked_azure_client (AzureClient): mocked azure client
    """
    # Mock container client
    mock_container_client = mock_blob_service.get_container_client.return_value

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    mock_blob_client.exists.return_value = True

    mock_az_storage = AzureStorage("testaccount", "test-rg")
    mock_az_storage.az_client = mocked_azure_client
    assert mock_az_storage.container_exists("testcontainer")


def test_container_does_not_exists(
    mock_blob_service: BlobServiceClient, mocked_azure_client: AzureClient
):
    """Test that the method returns False when a container does not exist.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
        mocked_azure_client (AzureClient): mocked azure client
    """
    # Mock container client
    mock_container_client = mock_blob_service.get_container_client.return_value

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    mock_blob_client.exists.return_value = False

    mock_az_storage = AzureStorage("testaccount", "test-rg")
    mock_az_storage.az_client = mocked_azure_client
    assert mock_az_storage.container_exists("testcontainer")


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
    # Create a test set of azure files for mocking the return value of list_blob_names method
    test_azure_files = {"file_not_exist"}

    # Create temp files inside temp directory
    for i in range(1, 3):
        tmp_file = os.path.join(matcha_testing_directory, f"temp{i}.txt")
        test_azure_files.add(tmp_file)
        with open(tmp_file, "w"):
            pass

    # Mock container client
    mock_container_client = mock_blob_service.get_container_client.return_value

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    # Mock container client list_blob_names() method, only 1 file to delete
    mock_container_client.list_blob_names.return_value = test_azure_files

    mock_az_storage = AzureStorage("testaccount", "test-rg")
    mock_az_storage.az_client = mocked_azure_client
    # Mock _get_container_client function of AzureStorage class
    with patch.object(AzureStorage, "_get_container_client") as mock_fn:
        mock_fn.return_value = mock_container_client
        mock_az_storage.upload_folder("testcontainer", matcha_testing_directory)

        # Check if upload_blob function is called
        mock_blob_client.upload_blob.assert_called()

        # Check if list_blob_names function is called
        mock_container_client.list_blob_names.assert_called()

        # Check if delete_blob function is called
        mock_container_client.delete_blob.assert_called()

        # Check if upload_blob function is called exactly twice
        assert mock_blob_client.upload_blob.call_count == len(
            os.listdir(matcha_testing_directory)
        )

        # Check if the delete_blob function is called exactly once as only one file does not exist
        assert mock_container_client.delete_blob.call_count == 1


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
    matcha_remote_state_dir = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "remote_state_storage"
    )
    matcha_resources_dir = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "resources"
    )
    os.makedirs(matcha_remote_state_dir, exist_ok=True)
    os.makedirs(matcha_resources_dir, exist_ok=True)
    os.chdir(matcha_testing_directory)

    assert os.path.exists(matcha_resources_dir)
    assert os.path.exists(matcha_remote_state_dir)

    # Create a test set of azure files for mocking the return value of list_blobs method
    files_on_azure = {"file_only_exist_azure"}

    # Create temp files inside temp directory
    for i in range(1, 3):
        tmp_file = os.path.join(matcha_resources_dir, f"temp{i}.txt")
        with open(tmp_file, "w"):
            pass

    # Mock container client
    mock_container_client = mock_blob_service.get_container_client.return_value

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    # Mock list blobs function for container client
    mock_container_client.list_blobs.return_value = [
        BlobProperties(name=n) for n in files_on_azure
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

        # Check that there are only 1 files in local
        assert len(os.listdir(matcha_testing_directory)) == 1


def test_create_empty(mock_blob_service: BlobServiceClient) -> None:
    """Test AzureStorage create_empty function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
    """
    # Mock container client
    mock_container_client = (
        mock_blob_service.return_value.get_container_client.return_value
    )

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    az_storage = AzureStorage("testaccount", "test-rg")
    az_storage.create_empty("testcontainer", "testblob")

    mock_blob_service.return_value.get_container_client.assert_called_once_with(
        "testcontainer"
    )
    mock_container_client.get_blob_client.assert_called_once_with("testblob")
    mock_blob_client.upload_blob.assert_called_once_with(
        data=""
    )  # Check that blob is uploaded and empty


def test_blob_exists(mock_blob_service: BlobServiceClient) -> None:
    """Test AzureStorage blob_exists function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
    """
    # Mock container client
    mock_container_client = (
        mock_blob_service.return_value.get_container_client.return_value
    )

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    az_storage = AzureStorage("testaccount", "test-rg")

    mock_blob_client.exists.return_value = True
    assert az_storage.blob_exists("testcontainer", "testblob")

    mock_blob_service.return_value.get_container_client.assert_called_with(
        "testcontainer"
    )
    mock_container_client.get_blob_client.assert_called_with("testblob")
    mock_blob_client.exists.assert_called_once()


def test_blob_does_not_exist(mock_blob_service: BlobServiceClient) -> None:
    """Test AzureStorage blob_exists function, when blob does not exist.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
    """
    # Mock container client
    mock_container_client = (
        mock_blob_service.return_value.get_container_client.return_value
    )

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    az_storage = AzureStorage("testaccount", "test-rg")

    mock_blob_client.exists.return_value = False
    assert not az_storage.blob_exists("testcontainer", "testblob")

    mock_blob_service.return_value.get_container_client.assert_called_with(
        "testcontainer"
    )
    mock_container_client.get_blob_client.assert_called_with("testblob")
    mock_blob_client.exists.assert_called_once()


def test_delete_blob(mock_blob_service: BlobServiceClient) -> None:
    """Test AzureStorage delete_blob function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
    """
    # Mock container client
    mock_container_client = (
        mock_blob_service.return_value.get_container_client.return_value
    )

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    az_storage = AzureStorage("testaccount", "test-rg")

    az_storage.delete_blob("testcontainer", "testblob")

    mock_blob_service.return_value.get_container_client.assert_called_with(
        "testcontainer"
    )
    mock_container_client.get_blob_client.assert_called_with("testblob")
    mock_blob_client.delete_blob.assert_called_once_with()  # Check that blob is uploaded and empty


def test_get_blob_names(mock_blob_service: BlobServiceClient) -> None:
    """Test that the get_blobs function return the expected result.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client.
    """
    # Mock container client
    mock_container_client = (
        mock_blob_service.return_value.get_container_client.return_value
    )

    mock_list_blob_names = mock_container_client.list_blob_names

    mock_list_blob_names.return_value = ["test_blob_name_1", "test_blob_name_2"]

    az_storage = AzureStorage("testaccount", "test-rg")

    result = az_storage._get_blob_names("testcontainer")

    mock_container_client.list_blob_names.assert_called_once()

    # Test that result returned is a set
    assert isinstance(result, set)

    # Test the result has expected value
    assert result == {"test_blob_name_1", "test_blob_name_2"}


def test_sync_remote(mock_blob_service: BlobServiceClient) -> None:
    """Test that sync remote removes the expected the blob.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client.
    """
    # Mock container client
    mock_container_client = (
        mock_blob_service.return_value.get_container_client.return_value
    )

    mock_blob_set = {"blob_1"}

    _ = mock_container_client.delete_blob.return_value

    az_storage = AzureStorage("testaccount", "test-rg")

    az_storage._sync_remote("testcontainer", mock_blob_set)

    mock_container_client.delete_blob.assert_called_once_with("blob_1")


def test_sync_local(
    mock_blob_service: BlobServiceClient, matcha_testing_directory: str
) -> None:
    """Test that sync local removes the matcha directory.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client.
        matcha_testing_directory (str): Path to the matcha testing directory.
    """
    matcha_remote_state_dir = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "remote_state_storage"
    )
    matcha_resources_dir = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "resources"
    )
    matcha_resources_tf_cache_dir = os.path.join(matcha_resources_dir, ".terraform")
    matcha_remote_state_tf_cache_dir = os.path.join(matcha_resources_dir, ".terraform")
    test_file_path = os.path.join(matcha_resources_dir, "temp.txt")

    os.makedirs(matcha_remote_state_dir, exist_ok=True)
    os.makedirs(matcha_resources_dir, exist_ok=True)
    os.makedirs(matcha_resources_tf_cache_dir, exist_ok=True)
    os.makedirs(matcha_remote_state_tf_cache_dir, exist_ok=True)
    with open(test_file_path, "w"):
        pass
    os.chdir(matcha_testing_directory)

    assert os.path.exists(matcha_resources_dir)
    assert os.path.exists(matcha_remote_state_dir)
    assert os.path.exists(matcha_resources_tf_cache_dir)
    assert os.path.exists(matcha_remote_state_tf_cache_dir)
    assert os.path.exists(test_file_path)

    az_storage = AzureStorage("testaccount", "test-rg")
    az_storage._sync_local(matcha_resources_dir)

    # Check if terraform cache are not deleted
    assert os.path.exists(matcha_resources_tf_cache_dir)
    assert os.path.exists(matcha_remote_state_tf_cache_dir)
    assert not os.path.exists(test_file_path)
