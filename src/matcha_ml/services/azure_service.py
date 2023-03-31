"""The Azure Service interface."""
from subprocess import DEVNULL

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.mgmt.resource import (
    ResourceManagementClient,
    SubscriptionClient,
)

from matcha_ml.errors import MatchaAuthenticationError


class AzureClient:
    """Azure client object to handle authentication checks and other Azure related functionality."""

    def __init__(self) -> None:
        """Constructor for the Azure Client object."""
        self.authenticated = self._authenticate()
        self.subscription_id = self._subscription_id()

    def _authenticate(self) -> bool:
        """Check whether the user is authenticated with 'az login'.

        Raises:
            MatchaAuthenticationError: when the Azure CLI is unable to be invoked.
            MatchaAuthenticationError: when no access token is recieved.

        Returns:
            bool: True if the checks pass, an error is raised otherwise.
        """
        self._credential = AzureCliCredential()
        self._client = SubscriptionClient(self._credential)

        try:
            self._credential.get_token(
                "https://management.azure.com/.default", stdout=DEVNULL
            )
        except CredentialUnavailableError:
            raise MatchaAuthenticationError("unable to invoke the Azure CLI")
        except ClientAuthenticationError:
            raise MatchaAuthenticationError("no access token recieved")

        return True

    def _subscription_id(self) -> str:
        """Fetch the subscription id.

        Returns:
            str: the subscription id.
        """
        return str(list(self._client.subscriptions.list())[0].subscription_id)

    def fetch_resource_group_names(self) -> set[str]:
        """Fetch the resource group names for the current subscription_id.

        Needed to check for duplication.

        Returns:
            Set[str]: the set of resource groups the user has provisioned.
        """
        if hasattr(self, "resource_group_names"):
            return self.resource_group_names  # type: ignore
        else:
            self._resource_client = ResourceManagementClient(
                self._credential, str(self._subscription_id)
            )
            self.resource_group_names = {
                resource_group.name
                for resource_group in self._resource_client.resource_groups.list()
            }
            return self.resource_group_names

    def fetch_regions(self) -> set[str]:
        """Fetch the Azure regions.

        Returns:
            set[str]: the set of all Azure regions.
        """
        if hasattr(self, "regions"):
            return self.regions  # type: ignore
        else:
            self.regions = {
                region.name
                for region in self._client.subscriptions.list_locations(
                    self.subscription_id
                )
            }
            return self.regions

    def is_valid_region(self, region: str) -> bool:
        """Check whether the user inputted region is valid.

        Args:
            region (str): the user inputted region.

        Returns:
            bool: True/False depending on validity.
        """
        return region in self.fetch_regions()

    def is_valid_resource_group(self, rg_name: str) -> bool:
        """Check whether the user inputted resource group name is valid.

        Args:
            rg_name (str): the user inputted resource group name.

        Returns:
            bool: True/False depending on validity
        """
        return f"{rg_name}-resources" not in self.fetch_resource_group_names()
