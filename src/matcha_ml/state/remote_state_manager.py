"""Remote state manager module."""
import contextlib
import dataclasses
import os.path
from typing import Iterator, Optional

from dataclasses_json import DataClassJsonMixin

from matcha_ml.errors import MatchaError
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

    _azure_storage: Optional[AzureStorage] = None

    config_path: str

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialise Remote State Manager."""
        if config_path is not None:
            self.config_path = config_path
        else:
            self.config_path = os.path.join(os.getcwd(), DEFAULT_CONFIG_NAME)

    def _configuration_file_exists(self) -> bool:
        return os.path.exists(self.config_path)

    def _load_configuration(self) -> RemoteStateConfig:
        with open(self.config_path) as f:
            return RemoteStateConfig.from_json(f.read())

    @property
    def configuration(self) -> RemoteStateConfig:
        """Configuration property.

        Returns:
            RemoteStateConfig: configuration read from the file system
        """
        try:
            return self._load_configuration()
        except Exception as e:
            raise MatchaError(f"Error while loading state configuration: {e}")

    @property
    def azure_storage(self) -> AzureStorage:
        """Azure Storage property.

        If it was not initialized before, it will be initialized

        Returns:
            AzureStorage: to interact with blob storage on Azure
        """
        if self._azure_storage is None:
            try:
                self._azure_storage = AzureStorage(
                    self.configuration.remote_state_bucket.account_name,
                    self.configuration.remote_state_bucket.client_id,
                )
            except Exception as e:
                raise MatchaError(f"Error while creating Azure Storage client: {e}")

        return self._azure_storage

    def _bucket_exists(self, container_name: str) -> bool:
        return self.azure_storage.container_exists(container_name)

    def is_state_provisioned(self) -> bool:
        """Check if remote state has already been provisioned.

        Returns:
            bool: is state provisioned
        """
        if not self._configuration_file_exists():
            return False

        if not self._bucket_exists(
            self.configuration.remote_state_bucket.container_name
        ):
            return False

        return True

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
