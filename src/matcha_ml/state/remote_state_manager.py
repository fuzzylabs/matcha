"""Remote state manager module."""
import contextlib
import dataclasses
from typing import Iterator, Optional

from dataclasses_json import DataClassJsonMixin

from matcha_ml.storage import AzureStorage

DEFAULT_CONFIG_NAME = "matcha.config.json"


@dataclasses.dataclass
class RemoteStateBucketConfig(DataClassJsonMixin):
    """Dataclass to store state bucket configuration."""

    # Azure storage account name
    account_name: str

    # Azure storage container name
    container_name: str

    # Azure Managed Identity client ID
    client_id: str


@dataclasses.dataclass
class RemoteStateConfig(DataClassJsonMixin):
    """Dataclass to store remote state configuration."""

    remote_state_bucket: RemoteStateBucketConfig


class RemoteStateManager:
    """Remote State Manager class.

    This class is used to interact with the remote Matcha state.
    """

    config_path: str

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialise Remote State Manager."""
        ...

    @property
    def configuration(self) -> RemoteStateConfig:
        """Configuration property.

        Returns:
            RemoteStateConfig: configuration read from the file system
        """
        return RemoteStateConfig(
            remote_state_bucket=RemoteStateBucketConfig(
                account_name="", container_name="", client_id=""
            )
        )

    @property
    def azure_storage(self) -> AzureStorage:
        """Azure Storage property.

        Returns:
            AzureStorage: to interact with blob storage on Azure
        """
        return AzureStorage("", "")

    def is_state_provisioned(self) -> bool:
        """Check if remote state has been provisioned.

        Returns:
            bool: True if the remote state is provisioned.
        """
        return False

    def provision_state_storage(
        self, location: str, prefix: str, verbose: Optional[bool] = False
    ) -> None:
        """Provision the state bucket using templates.

        Args:
            location (str): location of where this bucket will be provisioned
            prefix (str): Prefix used for all resources, or empty string to fill in.
            verbose (Optional[bool], optional): additional output is show when True. Defaults to False.
        """
        ...

    def deprovision_state_storage(self) -> None:
        """Destroy the state bucket provisioned."""
        ...

    def download(self) -> None:
        """Download the remote state into the local matcha state directory."""
        ...

    def upload(self) -> None:
        """Upload the local matcha state to the remote state storage."""
        ...

    @contextlib.contextmanager
    def use_remote_state(self) -> Iterator[None]:
        """Context manager to use remote state.

        Downloads the state before executing the code.
        Upload the state when context is finished.
        """
        yield
