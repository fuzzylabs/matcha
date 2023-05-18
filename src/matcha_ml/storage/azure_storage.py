"""Class to interact with Azure Storage."""
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient


class AzureStorage:
    """Class to interact with Azure blob storage."""

    account_name: str
    _account_url: str
    _credentials: TokenCredential
    blob_service_client: BlobServiceClient

    def __init__(self, account_name: str, client_id: str) -> None:
        """Initialize Azure Storage.

        Args:
            account_name: Azure storage account name
            client_id (str): Azure Managed identity client id
        """
        self.account_name = account_name
        self.client_id = client_id
        self._account_url = f"https://{account_name}.blob.core.windows.net"
        self._credentials = DefaultAzureCredential()
        self.blob_service_client = BlobServiceClient(
            account_url=self._account_url, credential=self._credentials
        )

    def _get_container_client(self, container_name: str) -> ContainerClient:
        return self.blob_service_client.get_container_client(container_name)

    def container_exists(self, container_name: str) -> bool:
        """Check if storage container exists.

        Args:
            container_name: Azure storage container name

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
