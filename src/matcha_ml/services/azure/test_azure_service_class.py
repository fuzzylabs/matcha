"""Temporary testing file for Azure Service DELETE LATER."""
from azure_service import AzureClient

from matcha_ml.errors import MatchaAuthenticationError

try:
    client = AzureClient()
    print(client.verify_azure_location("ukweeeeest"))
except MatchaAuthenticationError as e:
    print(e)
