"""Class to interact with Azure Storage."""
import glob
import hashlib
import os
import tempfile
from typing import Optional, Set

from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient

from matcha_ml.constants import LOCK_FILE_NAME
from matcha_ml.services.azure_service import AzureClient

IGNORE_FOLDERS = [".terraform"]


class AzureStorage:
    """Class to interact with Azure blob storage."""

    az_client: AzureClient
    blob_service_client: BlobServiceClient
    account_name: Optional[str] = None
    resource_group_name: Optional[str] = None

    def __init__(self, account_name: str, resource_group_name: str) -> None:
        """Initialize Azure Storage.

        Args:
            account_name (str): Azure storage account name
            resource_group_name (str): Name of resource group containing given account name
        """
        self.account_name = account_name
        self.resource_group_name = resource_group_name
        self.az_client = AzureClient()
        self.resource_group_exists = self.az_client.resource_group_exists(
            resource_group_name
        )
        if self.resource_group_exists:
            _conn_str = self.az_client.fetch_connection_string(
                storage_account_name=account_name,
                resource_group_name=resource_group_name,
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
        """Upload a folder to an Azure Storage Container and delete any files that are not present `src_folder_path`.

        Args:
            container_name (str): Azure storage container name
            src_folder_path (str): Path to folder to upload all files from
        """
        container_client = self._get_container_client(container_name)
        # Get all existing blobs
        blob_set = self._get_blob_names(container_name=container_name)

        for root, _, filenames in os.walk(src_folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)

                # ignore uploading files in IGNORE_FOLDERS
                if any(ignore_folder in file_path for ignore_folder in IGNORE_FOLDERS):
                    continue

                if file_path in blob_set:
                    blob_set.remove(file_path)

                blob_client = container_client.get_blob_client(blob=file_path)
                self.upload_file(blob_client, file_path)

        # Remove blobs that are not present in the local `src_folder_path``
        self._sync_remote(container_name=container_name, blob_set=blob_set)

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
        """Downloads a folder from Azure Storage Container.

        Local directory is cleared beforehand, ensuring that the local files match the remote files.

        Args:
            container_name (str): Azure storage container name
            dest_folder_path (str): Path to folder to download all the files
        """
        # Sync local matcha directory with remote storage
        matcha_resources_dir = os.path.join(".matcha", "infrastructure", "resources")
        self._sync_local(os.path.join(dest_folder_path, matcha_resources_dir))

        container_client = self._get_container_client(container_name)

        for blob in container_client.list_blobs():
            if LOCK_FILE_NAME in str(blob.name):
                continue
            blob_client = container_client.get_blob_client(blob=str(blob.name))
            file_path = os.path.join(dest_folder_path, str(blob.name))

            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

            self.download_file(blob_client, file_path)

    def _get_blob_client(self, container_name: str, blob_name: str) -> BlobClient:
        """Get a blob client by name.

        Args:
            container_name (str): Azure storage container name
            blob_name (str): blob name

        Returns:
            BlobClient: a blob client
        """
        return self._get_container_client(container_name).get_blob_client(blob_name)

    def create_empty(self, container_name: str, blob_name: str) -> None:
        """Create an empty blob in Azure Container.

        Args:
            container_name (str): Azure storage container name
            blob_name (str): blob name

        Raises:
            azure.core.exceptions.ResourceExistsError: when blob already exists
        """
        self._get_blob_client(container_name, blob_name).upload_blob(data="")

    def blob_exists(self, container_name: str, blob_name: str) -> bool:
        """Check whether a blob exists in a container.

        Args:
            container_name (str): Azure storage container name
            blob_name (str): blob name

        Returns:
            bool: True, if blob exists
        """
        return self._get_blob_client(container_name, blob_name).exists()

    def delete_blob(self, container_name: str, blob_name: str) -> None:
        """Delete blob by name.

        Args:
            container_name (str): Azure storage container name
            blob_name (str): blob name
        """
        self._get_blob_client(container_name, blob_name).delete_blob()

    def _get_blob_names(self, container_name: str) -> Set[str]:
        """A function for return a set of blob names.

        Args:
            container_name (str): the name of the blob container to look for blobs.

        Returns:
            Set[str]: a set of blob names in the container.
        """
        return set(self._get_container_client(container_name).list_blob_names())

    def get_hash_remote_state(self, container_name: str, blob_name: str) -> str:
        """Get hash of remote matcha state file.

        Args:
            container_name (str): Azure storage container name
            blob_name (str): blob name

        Returns:
            str: Hash contents of the blob in hexadecimal string
        """
        remote_hash = None
        blob_client = self._get_blob_client(
            container_name=container_name, blob_name=blob_name
        )
        with tempfile.NamedTemporaryFile() as tmp:
            self.download_file(blob_client, tmp.name)
            with open(tmp.name, "rb") as fp:
                remote_hash = hashlib.md5(fp.read()).hexdigest()
        return remote_hash

    def _sync_remote(self, container_name: str, blob_set: Set[str]) -> None:
        """Synchronizes the remote storage with the local files.

        It ignores uploading files in `.matcha` folder that are ignored in `IGNORED_FOLDERS`.

        Args:
            container_name (str): The name of the blob container to look for blobs.
            blob_set (Set[str]): Set of blob names to be removed on the remote storage.
        """
        container_client = self._get_container_client(container_name=container_name)

        # Remove blobs that are not present in the local `src_folder_path``
        for blob in blob_set:
            # Ensure that the lock file is not being prematurely removed from the remote bucket
            if LOCK_FILE_NAME in blob:
                continue
            container_client.delete_blob(blob)

    def _sync_local(self, dest_folder_path: str) -> None:
        """Synchronizes the local .matcha folder with the remote storage files.

        It ignores deleting files in `.matcha` folder that are not present in remote storage.

        Args:
            dest_folder_path (str): Path to folder containing matcha resources
        """
        # Clears the local matcha directory by removing all files,
        # ensuring that it exclusively contains the files retrieved from Azure remote storage
        if os.path.exists(dest_folder_path):
            matcha_template_dir = os.path.join(os.getcwd(), ".matcha")
            for path in glob.glob(f"{matcha_template_dir}/**/*", recursive=True):
                # ignore deleting folders ignored in IGNORE_FOLDERS
                if any(ignore_folder in path for ignore_folder in IGNORE_FOLDERS):
                    continue

                if os.path.isfile(path):
                    os.remove(path)
