"""Functions for uploading and downloading files to Azure storage bucket."""
import os
from azure.storage.blob import BlobServiceClient

az_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")


class AzureStorage:
    storage_container_name: str
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(az_connection_string)

    def upload_blob(self, local_folder_path: str):
        """_summary_

        Args:
            local_folder_path (str): _description_
        """
        ...

    def download_blob(self, remote_folder_path: str):
        ...
