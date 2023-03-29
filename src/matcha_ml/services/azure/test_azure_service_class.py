"""Temporary testing file for Azure Service DELETE LATER."""
from azure_service import AzureClient

client = AzureClient()
print(client.check_authentication())
print(client.get_available_regions())
