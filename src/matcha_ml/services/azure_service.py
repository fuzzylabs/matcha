"""The Azure Service interface."""
from subprocess import DEVNULL

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.mgmt.resource import (  # type: ignore
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
        self.resource_group_names = self._resource_group_names()

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

    def _resource_group_names(self) -> set[str]:
        """Fetch the resource group names for the current subscription_id.

        Needed to check for duplication.

        Returns:
            set[str]: the set of resource groups the user has provisioned.
        """
        self._resource_client = ResourceManagementClient(
            self._credential, self._subscription_id
        )
        return {
            resource_group.name
            for resource_group in self._resource_client.resource_groups.list()
        }

    def fetch_regions(self) -> set[str]:
        """Fetch the Azure regions.

        Returns:
            set[str]: the set of all Azure regions.
        """
        return {"ukwest", "uksouth"}

    def is_valid_region(self, region: str) -> bool:
        """Check whether the user inputted region is valid.

        Args:
            region (str): the user inputted region.

        Returns:
            bool: True/False depending on validity.
        """
        return region in self.fetch_regions()

        #     # try:

    #     #     self.credential.get_token("https://management.azure.com/.default")
    #     # except CredentialUnavailableError:
    #     #     raise MatchaAuthenticationError(service_name="Azure")

    # def __init__(self) -> None:
    #     """AzureClient constructor."""
    #     self.check_authentication()

    #     """
    #     add credential and client here rather than properties
    #     self._credential
    #     self.authenticate():
    #         self._credential =
    #         self._client =
    #     self._subscription_id = ?
    #     """

    # def check_authentication(self) -> None:
    #     """Checks Azure authentication.

    #     Raises:
    #         MatchaAuthenticationError: When the user is not authenticated with Azure.
    #     """
    #     home_directory = os.path.expanduser("~")
    #     azure_dir_path = os.path.join(home_directory, ".azure", "azureProfile.json")

    #     if not os.path.exists(azure_dir_path):
    #         # Raise error as Azure authentication directory does not exist
    #         raise MatchaAuthenticationError(service_name="Azure")

    #     data = json.load(codecs.open(azure_dir_path, "r", "utf-8-sig"))
    #     if not data["subscriptions"]:
    #         # Raise error as user is not authenticated using `az login`
    #         raise MatchaAuthenticationError(service_name="Azure")

    #     # Method 2, this prints an extra line from Azures subprocesses
    #     # try:
    #     #     self.credential.get_token("https://management.azure.com/.default")
    #     # except CredentialUnavailableError:
    #     #     raise MatchaAuthenticationError(service_name="Azure")

    # @property
    # def credential(self) -> AzureCliCredential:
    #     """The CLI credential property for an authenticated user.

    #     Returns:
    #         AzureCliCredential: AzureCliCredential belonging to the authenticated user.
    #     """
    #     return AzureCliCredential()

    # @property
    # def subscription_client(self) -> SubscriptionClient:
    #     """The subscription client for an authenticated user.

    #     Returns:
    #         SubscriptionClient: An object containing the subscriptions for the authenticated user.
    #     """
    #     return SubscriptionClient(self.credential)

    # def get_available_regions(self) -> set[str]:
    #     """Gets a list of available regions.

    #     Returns:
    #         set[str]: Set of Azure location strings
    #     """
    #     sub_list = self.subscription_client.subscriptions.list()

    #     for group in list(sub_list):
    #         # Get all locations for a subscription
    #         locations = {
    #             location.name
    #             for location in self.subscription_client.subscriptions.list_locations(
    #                 group.subscription_id
    #             )
    #         }
    #         break

    #     return locations

    # def verify_azure_location(self, location_name: str) -> tuple[bool, str]:
    #     """Verifies whether the provided resource location name exists in Azure.

    #     Args:
    #         location_name (str): User inputted location.

    #     Returns:
    #         bool: Returns True if location name is valid
    #         str: Closest valid location name
    #     """
    #     locations = self.get_available_regions()

    #     closest_match = difflib.get_close_matches(location_name, locations, n=1)

    #     is_valid = location_name in locations

    #     if is_valid:
    #         return is_valid, location_name
    #     else:
    #         closest_match = difflib.get_close_matches(location_name, locations, n=1)
    #         if closest_match:
    #             return is_valid, closest_match[0]
    #         else:
    #             return is_valid, ""
