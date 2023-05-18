"""Class to interact with Azure Storage."""
from azure.storage.blob import BlobClient


class AzureStorage:
    """Class to interact with Azure blob storage."""

    account_name: str

    def __init__(self, account_name: str, client_id: str) -> None:
        """Initialize Azure Storage.

        Args:
            account_name (str): Azure storage account name
            client_id (str): Azure Managed identity client id
        """
        ...

    def container_exists(self, container_name: str) -> bool:
        """Check if storage container exists.

        Args:
            container_name: Azure storage container name
        Returns:
            bool: does container exist.
        """
        return False

    def upload_file(self, blob_client: BlobClient, src_file: str) -> None:
        """Upload a file to Azure Storage Container.

        Args:
            blob_client (BlobClient): Container client
            src_file (str): Path to upload the file from
        """
        ...

    def upload_folder(self, container_name: str, src_folder_path: str) -> None:
        """Upload a folder to Azure Storage Container.

        Args:
            container_name (str): Azure storage container name
            src_folder_path (str): Path to folder to upload all files from
        """
        ...

    def download_file(self, blob_client: BlobClient, dest_file: str) -> None:
        """Download a file from Azure Storage Container.

        Args:
            blob_client (BlobClient): Container client
            dest_file (str): Path to download the file to.
        """
        ...

    def download_folder(self, container_name: str, dest_folder_path: str) -> None:
        """Download a folder from Azure Storage Container.

        Args:
            container_name (str): Azure storage container name
            dest_folder_path (str): Path to folder to download all the files
        """
        ...
