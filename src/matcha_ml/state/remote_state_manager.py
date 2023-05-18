"""Remote state manager module."""
import dataclasses
import os
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_step_success_status,
)
from matcha_ml.templates.build_templates.state_storage_template import (
    build_template,
    build_template_configuration,
)
from matcha_ml.templates.run_state_storage_template import TemplateRunner


@dataclasses.dataclass
class RemoteStateBucketConfig(DataClassJsonMixin):
    """Dataclass to store state bucket configuration."""

    account_name: str

    container_name: str


@dataclasses.dataclass
class RemoteStateConfig(DataClassJsonMixin):
    """Dataclass to store remote state configuration."""

    remote_state_bucket: RemoteStateBucketConfig


class RemoteStateManager:
    """Remote State Manager class.

    This class is used to interact with the remote Matcha state.
    """

    def __init__(self) -> None:
        """Initialise Remote State Manager."""
        ...

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

        account_name, container_name = template_runner.provision()
        self._write_matcha_config(account_name, container_name)

        print_status(build_step_success_status("Provisioning is complete!"))

    def deprovision_state_storage(self) -> None:
        """Destroy the state bucket provisioned."""
        # create a runner for deprovisioning resource with Terraform service.
        template_runner = TemplateRunner()

        template_runner.deprovision()
        print_status(build_step_success_status("Destroying state bucket is complete!"))

    def _write_matcha_config(self, account_name: str, container_name: str) -> None:
        """Write the outputs of the Terraform deployed state storage to a bucket config file.

        Args:
            account_name (str): the storage account name of the remote state storage provisioned.
            container_name (str): the container name of the remote state storage provisioned.
        """
        config_file_path = os.path.join(os.getcwd(), "matcha.config.json")

        remote_state_bucket_config = RemoteStateBucketConfig(
            account_name=account_name, container_name=container_name
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
