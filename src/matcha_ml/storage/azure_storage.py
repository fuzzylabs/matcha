"""Functions for uploading and downloading files to Azure storage bucket."""
import os
from azure.storage.blob import BlobServiceClient, ContainerClient

az_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")


class AzureStorage:
    storage_container_name: str
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(az_connection_string)

    def upload_file(self, blob_client: ContainerClient, src_file: str):
        """Upload a file to Azure Storage Container.

        Args:
            blob_client (ContainerClient): Container client
            src_file (str): Path to upload the file from.
        """
        with open(src_file, "wb") as blob_data:
            blob_client.upload_blob(blob_data)

    def upload_folder(self, src_folder_path: str):
        """Upload a folder to Azure Storage Container.

        Args:
            src_folder_path (str): Path to folder to upload all files from
        """

        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

        for root, _, filenames in os.walk(src_folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                blob_client = container_client.get_blob_client(blob=file_path)
                self.upload_file(blob_client, file_path)

    def download_file(self, blob_client: ContainerClient, destination_file: str):
        """Download a file from Azure Storage Container.

        Args:
            blob_client (ContainerClient): Container client
            destination_file (str): Path to download the file to.
        """
        with open(destination_file, "wb") as my_blob:
            blob_data = blob_client.download_blob()
            blob_data.readinto(my_blob)

    def download_folder(self, dest_folder_path: str):
        """Download a folder from Azure Storage Container.

        Args:
            dest_folder_path (str): Path to folder to download all the files
        """
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob.name)
            filename = blob.name.split("/")[-1]
            self.download_file(blob_client, os.path.join(dest_folder_path, filename))
