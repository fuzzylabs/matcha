"""Azure Storage tests."""
from unittest.mock import patch

from matcha_ml.storage import AzureStorage


def test_container_exists():
    """Test that the method returns True when a container exists."""
    class_stub = "matcha_ml.storage.azure_storage.BlobServiceClient"
    with patch(class_stub) as mock_client:
        mock_client_instance = mock_client.return_value
        mock_container_client_instance = (
            mock_client_instance.get_container_client.return_value
        )
        mock_container_client_instance.exists.return_value = True
        azure_storage = AzureStorage("testaccount", "testclientid")
        assert azure_storage.container_exists("testcontainer")


def test_container_does_not_exist():
    """Test that the method returns False when a container does not exist."""
    class_stub = "matcha_ml.storage.azure_storage.BlobServiceClient"
    with patch(class_stub) as mock_client:
        mock_client_instance = mock_client.return_value
        mock_container_client_instance = (
            mock_client_instance.get_container_client.return_value
        )
        mock_container_client_instance.exists.return_value = False
        azure_storage = AzureStorage("testaccount", "testclientid")
        assert not azure_storage.container_exists("testcontainer")
