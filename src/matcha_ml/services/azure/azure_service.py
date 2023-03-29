"""Azure Client service definition file."""
from __future__ import annotations

import difflib
import sys
from io import StringIO

import typer
from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.mgmt.resource import SubscriptionClient

from matcha_ml.errors import MatchaAuthenticationError


class AzureClient:
    """Azure client object to handle authentication checks and other Azure related functionality."""

    def __init__(self) -> None:
        """AzureClient constructor."""
        self.check_authentication()

    def check_authentication(self) -> None:
        """Checks Azure authentication.

        Raises:
            MatchaAuthenticationError: When the user is not authenticated with Azure.
        """
        try:
            self.credential.get_token("https://management.azure.com/.default")
        except CredentialUnavailableError:
            raise MatchaAuthenticationError(service_name="Azure")

    @property
    def credential(self) -> AzureCliCredential:
        """The CLI credential property for an authenticated user.

        Returns:
            AzureCliCredential: AzureCliCredential belonging to the authenticated user.
        """
        return AzureCliCredential()

    @property
    def subscription_client(self) -> SubscriptionClient:
        """The subscription client for an authenticated user.

        Returns:
            SubscriptionClient: An object containing the subscriptions for the authenticated user.
        """
        return SubscriptionClient(self.credential)

    def get_available_regions(self) -> set[str]:
        """Gets a list of available regions.

        Returns:
            set[str]: Set of Azure location strings
        """
        sub_list = self.subscription_client.subscriptions.list()

        for group in list(sub_list):
            # Get all locations for a subscription
            locations = set(
                [
                    location.name
                    for location in self.subscription_client.subscriptions.list_locations(
                        group.subscription_id
                    )
                ]
            )
            break

        return locations

    def verify_azure_location(self, location_name: str) -> tuple[bool, str]:
        """Verifies whether the provided resource location name exists in Azure.

        Args:
            location_name (str): User inputted location.

        Returns:
            bool: Returns True if location name is valid
            str: Closest valid location name
        """
        locations = self.get_available_regions()

        closest_match = difflib.get_close_matches(location_name, locations, n=1)

        is_valid = location_name in locations

        if not closest_match:
            return is_valid, ""
        else:
            return is_valid, closest_match[0]
