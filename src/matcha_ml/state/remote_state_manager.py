"""Remote state manager module."""
import contextlib
import dataclasses
import os
from typing import Iterator, Optional

from azure.core.exceptions import ResourceExistsError
from dataclasses_json import DataClassJsonMixin

from matcha_ml.cli.ui.print_messages import print_error, print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_step_success_status,
    build_warning_status,
)
from matcha_ml.constants import LOCK_FILE_NAME
from matcha_ml.errors import MatchaError
from matcha_ml.runners.remote_state_runner import RemoteStateRunner
from matcha_ml.storage import AzureStorage
from matcha_ml.templates import RemoteStateTemplate

DEFAULT_CONFIG_NAME = "matcha.config.json"
ALREADY_LOCKED_MESSAGE = (
    "Remote state is already locked, maybe someone else is using matcha?"
    " If you think this is a mistake, you can unlock the state by running 'matcha force-unlock'."
)


@dataclasses.dataclass
class RemoteStateBucketConfig(DataClassJsonMixin):
    """Dataclass to store state bucket configuration."""

    # Azure storage account name
    account_name: str

    # Azure storage container name
    container_name: str

    # Azure resource group name
    resource_group_name: str


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
        """Initialize Remote State Manager.

        Args:
            config_path (Optional[str]): optional configuration file path
        """
        if config_path is not None:
            self.config_path = config_path
        else:
            self.config_path = os.path.join(os.getcwd(), DEFAULT_CONFIG_NAME)

    def _configuration_file_exists(self) -> bool:
        """Check if the remote state configuration file exists.

        Returns:
            bool: True, if the configuration file exists
        """
        return os.path.exists(self.config_path)

    def _load_configuration(self) -> RemoteStateConfig:
        """Load configuration file.

        Returns:
            RemoteStateConfig: remote state configuration
        """
        with open(self.config_path) as f:
            return RemoteStateConfig.from_json(f.read())

    @property
    def configuration(self) -> RemoteStateConfig:
        """Configuration property.

        Returns:
            RemoteStateConfig: configuration read from the file system

        Raises:
            MatchaError: if configuration file failed to load.
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

        Raises:
            MatchaError: if Azure Storage client failed to create
        """
        if self._azure_storage is None:
            try:
                self._azure_storage = AzureStorage(
                    account_name=self.configuration.remote_state_bucket.account_name,
                    resource_group_name=self.configuration.remote_state_bucket.resource_group_name,
                )
            except Exception as e:
                raise MatchaError(f"Error while creating Azure Storage client: {e}")

        return self._azure_storage

    def _bucket_exists(self, container_name: str) -> bool:
        """Check if a bucket for remote state management exists.

        Args:
            container_name (str): Azure Storage container name

        Returns:
            bool: True, if the bucket exists
        """
        return self.azure_storage.container_exists(container_name)

    def _resource_group_exists(self) -> bool:
        """Check if an Azure resource group already exists.

        Returns:
            bool: True, if the resource group exists
        """
        return self.azure_storage.resource_group_exists

    def get_hash_remote_state(self, remote_path: str) -> str:
        """Get the hash of remote matcha state file.

        Args:
            remote_path (str) : Path to file on remote storage

        Returns:
            str: Hash content of file on remote storage in hexadecimal string
        """
        return self.azure_storage.get_hash_remote_state(
            self.configuration.remote_state_bucket.container_name, remote_path
        )

    def is_state_provisioned(self) -> bool:
        """Check if remote state has already been provisioned.

        Returns:
            bool: is state provisioned
        """
        if not self._configuration_file_exists():
            return False

        if not self._resource_group_exists():
            return False

        if not self._bucket_exists(
            self.configuration.remote_state_bucket.container_name
        ):
            return False

        return True

    def is_state_stale(self) -> bool:
        """Check if remote state has been destroyed.

        Returns:
            bool: True, if state is stale
        """
        return bool(
            self._configuration_file_exists() and not self._resource_group_exists()
        )

    def provision_remote_state(
        self, location: str, prefix: str, verbose: Optional[bool] = False
    ) -> None:
        """Provision the state bucket using templates.

        Args:
            location (str): location of where this bucket will be provisioned
            prefix (str): Prefix used for all resources, or empty string to fill in.
            verbose (Optional[bool], optional): additional output is show when True. Defaults to False.
        """
        template_runner = RemoteStateRunner()
        state_storage_template = RemoteStateTemplate()

        project_directory = os.getcwd()
        destination = os.path.join(
            project_directory, ".matcha", "infrastructure", "remote_state_storage"
        )
        template = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "infrastructure",
            "remote_state_storage",
        )

        config = state_storage_template.build_template_configuration(
            location=location, prefix=prefix
        )
        state_storage_template.build_template(config, template, destination, verbose)

        account_name, container_name, resource_group_name = template_runner.provision()
        self._write_matcha_config(account_name, container_name, resource_group_name)
        print_status(
            build_step_success_status(
                "Provisioning Matcha resource group and remote state is complete!"
            )
        )
        print()

    def deprovision_remote_state(self) -> None:
        """Destroy the state bucket provisioned."""
        # create a runner for deprovisioning resource with Terraform service.
        template_runner = RemoteStateRunner()

        template_runner.deprovision()
        self.remove_matcha_config()

    def _write_matcha_config(
        self, account_name: str, container_name: str, resource_group_name: str
    ) -> None:
        """Write the outputs of the Terraform deployed state storage to a bucket config file.

        Args:
            account_name (str): the storage account name of the remote state storage provisioned.
            container_name (str): the container name of the remote state storage provisioned.
            resource_group_name (str): Azure client ID.
        """
        remote_state_bucket_config = RemoteStateBucketConfig(
            account_name=account_name,
            container_name=container_name,
            resource_group_name=resource_group_name,
        )
        remote_state_config = RemoteStateConfig(
            remote_state_bucket=remote_state_bucket_config
        )

        matcha_config = remote_state_config.to_json(indent=4)

        with open(self.config_path, "w") as f:
            f.write(matcha_config)

        print_status(
            build_step_success_status(
                f"The matcha configuration is written to {self.config_path}"
            )
        )

    def remove_matcha_config(self) -> None:
        """Remove the matcha.config.json file."""
        try:
            os.remove(self.config_path)
            self._azure_storage = None
        except FileNotFoundError:
            print_error(
                f"Failed to remove the matcha.config.json file at {self.config_path}, file not found."
            )

    def download(self, dest_folder_path: str) -> None:
        """Download the remote state into the local matcha state directory.

        Args:
            dest_folder_path (str): Path to local matcha state directory
        """
        self.azure_storage.download_folder(
            container_name=self.configuration.remote_state_bucket.container_name,
            dest_folder_path=dest_folder_path,
        )

    def upload(self, local_folder_path: str) -> None:
        """Upload the local matcha state to the remote state storage.

        Args:
            local_folder_path (str): Path to local matcha state directory
        """
        self.azure_storage.upload_folder(
            container_name=self.configuration.remote_state_bucket.container_name,
            src_folder_path=local_folder_path,
        )

    @contextlib.contextmanager
    def use_remote_state(self, destroy: bool = False) -> Iterator[None]:
        """Context manager to use remote state.

        Downloads the state before executing the code.
        Upload the state when context is finished.

        Args:
            destroy (bool): Flag for whether the command being run is 'destroy' or not.
        """
        self.download(os.getcwd())

        yield None

        if not destroy:
            self.upload(os.path.join(".matcha", "infrastructure"))

    def lock(self) -> None:
        """Lock remote state.

        Raises:
            MatchaError: if the state is already locked
        """
        try:
            self.azure_storage.create_empty(
                container_name=self.configuration.remote_state_bucket.container_name,
                blob_name=LOCK_FILE_NAME,
            )
        except ResourceExistsError:
            raise MatchaError(ALREADY_LOCKED_MESSAGE)

    def unlock(self) -> None:
        """Unlock remote state."""
        if not self.azure_storage.blob_exists(
            container_name=self.configuration.remote_state_bucket.container_name,
            blob_name=LOCK_FILE_NAME,
        ):
            print_status(
                build_warning_status("Tried unlocking state, but it was not locked")
            )
            return
        else:
            self.azure_storage.delete_blob(
                container_name=self.configuration.remote_state_bucket.container_name,
                blob_name=LOCK_FILE_NAME,
            )

    @contextlib.contextmanager
    def use_lock(self, destroy: bool = False) -> Iterator[None]:
        """Context manager to lock state.

        Args:
            destroy (bool): Flag for whether the command being run is 'destroy' or not.
        """
        self.lock()
        try:
            yield
        finally:
            if not destroy:
                self.unlock()
