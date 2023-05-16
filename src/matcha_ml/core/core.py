"""The core functions for matcha."""
import os
from typing import Dict, Optional

from matcha_ml.cli._validation import get_command_validation
from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_step_success_status,
)
from matcha_ml.errors import MatchaError
from matcha_ml.state import MatchaStateService
from matcha_ml.templates.build_templates.state_storage_template import (
    build_template,
    build_template_configuration,
)
from matcha_ml.templates.run_state_storage_template import TemplateRunner


def get(
    resource_name: Optional[str],
    property_name: Optional[str],
) -> Dict[str, Dict[str, str]]:
    """Return the information of the provisioned resource based on the resource name specified.

    Return all resources if no resource name is specified.

    Args:
        resource_name (Optional[str]): name of the resource to get information for.
        property_name (Optional[str]): the property of the resource to get.

    Returns:
        Dict[str, Dict[str, str]]: the information of the provisioned resource.

    Raises:
        MatchaError: Raised when the matcha.state file does not exist
        MatchaInputError: Raised when the resource or property name does not exist in the matcha.state file
    """
    matcha_state_service = MatchaStateService()

    if not matcha_state_service.state_file_exists:
        raise MatchaError(
            f"Error: matcha.state file does not exist at {os.path.join(os.getcwd(), '.matcha', 'infrastructure')} . Please run 'matcha provision' before trying to get the resource."
        )

    if resource_name:
        get_command_validation(
            resource_name, matcha_state_service.get_resource_names(), "resource type"
        )

    if resource_name and property_name:
        get_command_validation(
            property_name,
            matcha_state_service.get_property_names(resource_name),
            "property",
        )

    result = matcha_state_service.fetch_resources_from_state_file(
        resource_name, property_name
    )

    return result


def provision_state_storage(location: str, verbose: Optional[bool] = False) -> None:
    """Provision the state bucket using templates.

    Args:
        location (str): location of where this bucket will be provisioned
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

    config = build_template_configuration(location)
    build_template(config, template, destination, verbose)

    template_runner.provision()
    print_status(build_step_success_status("Provisioning is complete!"))


def deprovision_state_storage() -> None:
    """Destroy the state bucket provisioned."""
    # create a runner for deprovisioning resource with Terraform service.
    template_runner = TemplateRunner()

    template_runner.deprovision()
    print_status(build_step_success_status("Destroying state bucket is complete!"))
