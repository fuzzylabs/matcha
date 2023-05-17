"""Class to interact with Azure Storage."""
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient


class AzureStorage:
    """Class to interact with Azure blob storage."""

    account_name: str
    _account_url: str
    _credentials: TokenCredential
    blob_service_client: BlobServiceClient

    def __init__(self, account_name: str) -> None:
        """Initialize Azure Storage.

        Args:
            account_name: Azure storage account name
        """
        self.account_name = account_name
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
