"""Azure Client service definition file."""
import difflib
import sys
from io import StringIO

import typer
from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.mgmt.resource import SubscriptionClient


class AzureClient:
    """Azure client object to handle authentication checks and other Azure related functionality."""

    def __init__(self) -> None:
        """AzureClient constructor."""
        is_authenticated = self.check_authentication()
        if is_authenticated:
            print("User is authenticated with Azure.")
        else:
            print("Error, user is not authentciated with Azure.")
            return
        self.set_cli_credential()
        self.set_subscription_client()

    def check_authentication(self) -> bool:
        """Checks Azure authentication.

        Returns:
            bool: True if user is authenticated
        """
        credential = AzureCliCredential()

        output = StringIO()
        # Redirect stdout and stderr to the StringIO object
        sys.stdout = output
        sys.stderr = output

        try:
            # Check authentication
            credential.get_token("https://management.azure.com/.default")
        except CredentialUnavailableError:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            print(
                "Error, Matcha couldn't authenticate you with Azure! Make sure to run 'az login' before trying to provision resources."
            )
            return False

        # Restore stdout and stderr to their original values
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        return True

    def set_cli_credential(self) -> None:
        """Sets the CLI credential for an authenticated user."""
        self.credential = AzureCliCredential()

    def get_cli_credential(self) -> AzureCliCredential:
        """Gets the the CLI credential for an authenticated user.

        Returns:
            AzureCliCredential: AzureCliCredential belonging to the authenticated user.
        """
        return self.credential

    def set_subscription_client(self) -> None:
        """Sets the subscription client for an authenticated user."""
        self.subscription_client = SubscriptionClient(self.credential)

    def get_subscription_client(self) -> SubscriptionClient:
        """Gets the subscription client for an authenticated user.

        Returns:
            SubscriptionClient: SubscriptionClient belonging to the authenticated user.
        """
        return self.subscription_client

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
