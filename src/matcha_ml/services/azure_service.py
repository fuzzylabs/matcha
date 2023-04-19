"""The Azure Service interface."""
from subprocess import DEVNULL
from typing import Optional, Set

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.mgmt.resource import (
    ResourceManagementClient,
    SubscriptionClient,
)

from matcha_ml.errors import MatchaAuthenticationError


class AzureClient:
    """Azure client object to handle authentication checks and other Azure related functionality."""

    _resource_group_names: Optional[Set[str]] = None
    _regions: Optional[Set[str]] = None

    def __init__(self) -> None:
        """Constructor for the Azure Client object."""
        self.authenticated = self._check_authentication()
        self.subscription_id = self._subscription_id()
        self._set_resource_groups()

    def _check_authentication(self) -> bool:
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
            raise MatchaAuthenticationError("no access token received")

        return True

    def _subscription_id(self) -> str:
        """Fetch the subscription id.

        Returns:
            str: the subscription id.
        """
        subscriptions = self._client.subscriptions.list()
        if subscriptions:
            return str(list(subscriptions)[0].subscription_id)
        else:
            raise MatchaAuthenticationError(
                "no subscriptions found - you at least one subscription active in your Azure account."
            )

    def _set_resource_groups(self) -> None:
        """Sets the value of resource groups as Azure ResourceGroup objects in a dictionary."""
        self._resource_client = ResourceManagementClient(
            self._credential, str(self.subscription_id)
        )
        self._resource_groups = {
            rg.name: rg for rg in self._resource_client.resource_groups.list()
        }

    def fetch_resource_group_names(self) -> Set[str]:
        """Fetch the resource group names for the current subscription_id.

        Needed to check for duplication.

        Returns:
            Set[str]: the set of resource groups the user has provisioned.
        """
        return set(self._resource_groups.keys())

    def resource_group_state(self, resource_group_name: str) -> str:
        """Gets the resource group state.

        Args:
            resource_group_name (str): the user inputted resource group name.

        Returns:
            str: Resource group status.
        """
        if resource_group_name in self._resource_groups:
            return str(
                self._resource_groups[resource_group_name].properties.provisioning_state
            )
        else:
            return "Not Provisioned"

    def fetch_regions(self) -> Set[str]:
        """Fetch the Azure regions.

        Returns:
            set[str]: the set of all Azure regions.
        """
        if self._regions:
            return self._regions
        else:
            self._regions = {
                region.name
                for region in self._client.subscriptions.list_locations(
                    self.subscription_id
                )
            }
            return self._regions

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
