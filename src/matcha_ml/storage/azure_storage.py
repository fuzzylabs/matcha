"""Functions for uploading and downloading files to Azure storage bucket."""
import os
from azure.storage.blob import BlobServiceClient, ContainerClient

az_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")


class AzureStorage:
    storage_container_name: str
    blob_service_client: BlobServiceClient = None
    container_client: ContainerClient = None

    def __init__(self, storage_container_name: str) -> None:
        """Initialize AzureStorage.

        Args:
            storage_container_name (str): Name of the storage container
        """
        self.storage_container_name = storage_container_name

        # Create the BlobServiceClient object
        self.blob_service_client = BlobServiceClient.from_connection_string(
            az_connection_string
        )

        # Get the ContainerClient object for given container name
        self.container_client = self.blob_service_client.get_container_client(
            self.storage_container_name
        )

    def upload_file(self, blob_client: ContainerClient, src_file: str):
        """Upload a file to Azure Storage Container.

        Args:
            blob_client (ContainerClient): Container client
            src_file (str): Path to upload the file from.
        """
        with open(src_file, "rb") as blob_data:
            blob_client.upload_blob(blob_data)

    def upload_folder(self, src_folder_path: str):
        """Upload a folder to Azure Storage Container.

        Args:
            src_folder_path (str): Path to folder to upload all files from
        """
        for root, _, filenames in os.walk(src_folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                blob_client = self.container_client.get_blob_client(blob=file_path)
                self.upload_file(blob_client, file_path)

    def download_file(self, blob_client: ContainerClient, dest_file: str):
        """Download a file from Azure Storage Container.

        Args:
            blob_client (ContainerClient): Container client
            dest_file (str): Path to download the file to.
        """
        with open(dest_file, "wb") as my_blob:
            blob_data = blob_client.download_blob()
            blob_data.readinto(my_blob)

    def download_folder(self, dest_folder_path: str):
        """Download a folder from Azure Storage Container.

        Args:
            dest_folder_path (str): Path to folder to download all the files
        """
        for blob in self.container_client.list_blobs():
            blob_client = self.container_client.get_blob_client(blob.name)
            file_path = os.path.join(dest_folder_path, blob.name)
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self.download_file(blob_client, file_path)
