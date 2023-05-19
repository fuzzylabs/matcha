"""Remote state manager module."""
import contextlib
import dataclasses
import os
from typing import Iterator, Optional

from dataclasses_json import DataClassJsonMixin

from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_step_success_status,
)
from matcha_ml.storage import AzureStorage
from matcha_ml.templates.build_templates.state_storage_template import (
    build_template,
    build_template_configuration,
)
from matcha_ml.templates.run_state_storage_template import TemplateRunner

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
        template_runner = TemplateRunner()

        project_directory = os.getcwd()
        destination = os.path.join(
            project_directory, ".matcha", "infrastructure/remote_state_storage"
        )
        template = os.path.join(
            os.path.dirname(__file__), os.pardir, "infrastructure/remote_state_storage"
        )

        config = build_template_configuration(location, prefix)
        build_template(config, template, destination, verbose)

        account_name, container_name, client_id = template_runner.provision()
        self._write_matcha_config(account_name, container_name, client_id)

        print_status(build_step_success_status("Provisioning is complete!"))

    def deprovision_state_storage(self) -> None:
        """Destroy the state bucket provisioned."""
        # create a runner for deprovisioning resource with Terraform service.
        template_runner = TemplateRunner()

        template_runner.deprovision()
        print_status(
            build_step_success_status("Destroying remote state management is complete!")
        )

    def _write_matcha_config(
        self, account_name: str, container_name: str, client_id: str
    ) -> None:
        """Write the outputs of the Terraform deployed state storage to a bucket config file.

        Args:
            account_name (str): the storage account name of the remote state storage provisioned.
            container_name (str): the container name of the remote state storage provisioned.
            client_id (str): Azure client ID.
        """
        config_file_path = os.path.join(os.getcwd(), "matcha.config.json")

        remote_state_bucket_config = RemoteStateBucketConfig(
            account_name=account_name,
            container_name=container_name,
            client_id=client_id,
        )
        remote_state_config = RemoteStateConfig(
            remote_state_bucket=remote_state_bucket_config
        )

        matcha_config = remote_state_config.to_json(indent=4)

        with open(config_file_path, "w") as f:
            f.write(matcha_config)

        print_status(
            build_step_success_status(
                f"The matcha configuration is written to {config_file_path}"
            )
        )

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
