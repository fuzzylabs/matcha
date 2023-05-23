"""Class to interact with Azure Storage."""
import os

from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient

from matcha_ml.services.azure_service import AzureClient


class AzureStorage:
    """Class to interact with Azure blob storage."""

    az_client: AzureClient
    blob_service_client: BlobServiceClient

    def __init__(self, account_name: str, resource_group_name: str) -> None:
        """Initialize Azure Storage.

        Args:
            account_name (str): Azure storage account name
            resource_group_name (str): Name of resource group containing given account name
        """
        self.az_client = AzureClient()
        _conn_str = self.az_client.fetch_connection_string(
            storage_account_name=account_name, resource_group_name=resource_group_name
        )
        self.blob_service_client = BlobServiceClient.from_connection_string(
            conn_str=_conn_str
        )

    def _get_container_client(self, container_name: str) -> ContainerClient:
        """Get a container client using container name.

        Args:
            container_name (str): Azure storage container name

        Returns:
            ContainerClient: Container client for given container.
        """
        return self.blob_service_client.get_container_client(container_name)

    def container_exists(self, container_name: str) -> bool:
        """Check if storage container exists.

        Args:
            container_name (str): Azure storage container name

        Returns:
            bool: does container exist
        """
        container_client = self._get_container_client(container_name)

        return container_client.exists()

    def upload_file(self, blob_client: BlobClient, src_file: str) -> None:
        """Upload a file to Azure Storage Container.

        Args:
            blob_client (BlobClient): Container client
            src_file (str): Path to upload the file from
        """
        with open(src_file, "rb") as blob_data:
            blob_client.upload_blob(data=blob_data, overwrite=True)

    def upload_folder(self, container_name: str, src_folder_path: str) -> None:
        """Upload a folder to Azure Storage Container.

        Args:
            container_name (str): Azure storage container name
            src_folder_path (str): Path to folder to upload all files from
        """
        container_client = self._get_container_client(container_name)

        for root, _, filenames in os.walk(src_folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                blob_client = container_client.get_blob_client(blob=file_path)
                self.upload_file(blob_client, file_path)

    def download_file(self, blob_client: BlobClient, dest_file: str) -> None:
        """Download a file from Azure Storage Container.

        Args:
            blob_client (BlobClient): Container client
            dest_file (str): Path to download the file to
        """
        with open(dest_file, "wb") as my_blob:
            blob_data = blob_client.download_blob()
            blob_data.readinto(my_blob)

    def download_folder(self, container_name: str, dest_folder_path: str) -> None:
        """Download a folder from Azure Storage Container.

        Args:
            container_name (str): Azure storage container name
            dest_folder_path (str): Path to folder to download all the files
        """
        container_client = self._get_container_client(container_name)

        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob=str(blob.name))
            file_path = os.path.join(dest_folder_path, str(blob.name))
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self.download_file(blob_client, file_path)
