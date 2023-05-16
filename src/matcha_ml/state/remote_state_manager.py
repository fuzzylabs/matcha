"""Remote state manager module."""
import dataclasses
import os
from typing import Optional, Tuple

import typer

from matcha_ml.cli._validation import prefix_typer_callback, region_typer_callback
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
class RemoteStateBucketConfig:
    """Dataclass to store state bucket configuration."""

    container_name: str


@dataclasses.dataclass
class RemoteStateConfig:
    """Dataclass to store remote state configuration."""

    remote_state_bucket: RemoteStateBucketConfig


class RemoteStateManager:
    """Remote State Manager class.

    This class is used to interact with the remote Matcha state.
    """

    def __init__(self) -> None:
        """Initialise Remote State Manager."""
        ...

    def fill_provision_variables(
        self,
        location: str,
        prefix: str,
    ) -> Tuple[str, str]:
        """Prompt for the provision variables if they were not provided.

        Args:
            location (str): Azure location in which all resources will be provisioned, or empty string to fill in.
            prefix (str): Prefix used for all resources, or empty string to fill in.

        Returns:
            Tuple[str, str]: A tuple of location and prefix which were filled in
        """
        if not location:
            location = typer.prompt(
                default=None,
                text="What region should your resources be provisioned in (e.g., 'ukwest')?",
                value_proc=region_typer_callback,
            )
        if not prefix:
            prefix = typer.prompt(
                text="Your resources need a name (an alphanumerical prefix; 3-11 character limit), what should matcha call them?",
                default="matcha",
                value_proc=prefix_typer_callback,
            )

        return location, prefix

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

        location, prefix = self.fill_provision_variables(location, prefix)
        config = build_template_configuration(location, prefix)
        build_template(config, template, destination, verbose)

        template_runner.provision()
        print_status(build_step_success_status("Provisioning is complete!"))

    def deprovision_state_storage(self) -> None:
        """Destroy the state bucket provisioned."""
        # create a runner for deprovisioning resource with Terraform service.
        template_runner = TemplateRunner()

        template_runner.deprovision()
        print_status(build_step_success_status("Destroying state bucket is complete!"))
