"""The Azure Service interface."""
from subprocess import DEVNULL
from typing import Dict, Optional, Set, cast

import jwt
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.confluent.models._confluent_management_client_enums import (  # type: ignore [import]
    ProvisionState,
)
from azure.mgmt.resource import (
    ResourceManagementClient,
    SubscriptionClient,
)
from azure.mgmt.resource.resources.models import ResourceGroup

from matcha_ml.errors import MatchaAuthenticationError, MatchaPermissionError

ROLE_ID_MAPPING = {
    "Owner": "8e3af657-a8ff-443c-a75c-2fe8c4bcb635",
    "Contributor": "b24988ac-6180-42a0-ab88-20f7382dd24c",
    "User Access Administrator": "18d7d88d-d35e-4fb5-a5c3-7773c20a72d9",
}

ACCEPTED_ROLE_CONFIGURATIONS = [["Owner"], ["Contributor", "User Access Administrator"]]


class AzureClient:
    """Azure client object to handle authentication checks and other Azure related functionality."""

    _regions: Optional[Set[str]] = None
    _access_token: Optional[AccessToken] = None
    _resource_groups: Optional[Dict[str, ResourceGroup]] = None

    def __init__(self) -> None:
        """Constructor for the Azure Client object."""
        self.authenticated = self._check_authentication()
        self.subscription_id = self._subscription_id()
        self.has_permissions = self._check_required_role_assignments()

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
            self._access_token = self._credential.get_token(
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

    def _get_principal_id(self) -> str:
        """Get principal ID of the authenticated user.

        Returns:
            str: principal ID
        """
        if self._access_token is None:
            raise MatchaAuthenticationError(
                "internal error: the client needs to be authenticated first"
            )

        decoded_token = jwt.decode(
            self._access_token.token,
            options={"verify_signature": False},
            algorithms=["RS256"],
        )
        user_object_id = cast(str, decoded_token["oid"])

        return user_object_id

    def _check_required_role_assignments(self) -> bool:
        """Check if the user has one of the required sets of roles.

        Returns:
            bool: True if required roles are assigned

        Raises:
            MatchaPermissionError: when the user does not have required roles

        """
        self._authorization_client = AuthorizationManagementClient(
            self._credential, self.subscription_id
        )
        principal_id = self._get_principal_id()
        role_assignments = (
            self._authorization_client.role_assignments.list_for_subscription()
        )
        roles = [
            x.role_definition_id
            for x in role_assignments
            if x.principal_id == principal_id
        ]

        for role_configuration in ACCEPTED_ROLE_CONFIGURATIONS:
            expected_roles = [
                f"/subscriptions/{self.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{ROLE_ID_MAPPING[role]}"
                for role in role_configuration
            ]
            if all([role in roles for role in expected_roles]):
                return True
        raise MatchaPermissionError(
            f"Error - Matcha detected that you do not have the appropriate role-based permissions on Azure to run this action. You need one of the following role configurations: {ACCEPTED_ROLE_CONFIGURATIONS} note: list items containing multiple roles require all of the listed roles."
        )

    def fetch_resource_groups(self) -> Dict[str, ResourceGroup]:
        """Fetches the value of resource groups as Azure ResourceGroup objects in a dictionary.

        Returns:
            Dict[str, ResourceGroup]: A dictionary with resource group name as the key its corresponding object
        """
        if self._resource_groups:
            return self._resource_groups
        else:
            self._resource_client = ResourceManagementClient(
                self._credential, str(self.subscription_id)
            )
            self._resource_groups = {
                rg.name: rg for rg in self._resource_client.resource_groups.list()
            }

            return self._resource_groups

    def fetch_resource_group_names(self) -> Set[str]:
        """Fetch the resource group names for the current subscription_id.

        Needed to check for duplication.

        Returns:
            Set[str]: the set of resource groups the user has provisioned.
        """
        return set(self.fetch_resource_groups().keys())

    def resource_group_state(
        self, resource_group_name: str
    ) -> Optional[ProvisionState]:
        """Gets the resource group state.

        Args:
            resource_group_name (str): the user inputted resource group name.

        Returns:
            ProvisionState: Resource group Enum state if it exists.
        """
        if resource_group_name in self.fetch_resource_groups():
            resource_group = self.fetch_resource_groups()[resource_group_name]
            if (
                isinstance(resource_group, ResourceGroup)
                and resource_group.properties is not None
            ):
                return ProvisionState[resource_group.properties.provisioning_state]

        return None

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
