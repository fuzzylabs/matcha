"""The core functions for matcha."""
import os
from typing import Optional

from matcha_ml.cli._validation import get_command_validation
from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.cli.ui.status_message_builders import build_warning_status
from matcha_ml.core._validation import is_valid_prefix, is_valid_region
from matcha_ml.errors import MatchaError, MatchaInputError
from matcha_ml.runners import AzureRunner
from matcha_ml.services.analytics_service import AnalyticsEvent, track
from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.state import MatchaStateService, RemoteStateManager
from matcha_ml.state.matcha_state import MatchaState
from matcha_ml.templates.azure_template import AzureTemplate


@track(event_name=AnalyticsEvent.GET)
def get(
    resource_name: Optional[str],
    property_name: Optional[str],
) -> MatchaState:
    """Return the information of the provisioned resource based on the resource name specified.

    Return all resources if no resource name is specified.

    Args:
        resource_name (Optional[str]): name of the resource to get information for.
        property_name (Optional[str]): the property of the resource to get.

    Returns:
        MatchaState: the information of the provisioned resource.

    Raises:
        MatchaError: Raised when the matcha state has not been initialized
        MatchaError: Raised when the matcha.state file does not exist
        MatchaInputError: Raised when the resource or property name does not exist in the matcha.state file
    """
    matcha_state_service = MatchaStateService()
    remote_state = RemoteStateManager()

    if not remote_state.is_state_provisioned():
        raise MatchaError(
            "Error - matcha state has not been initialized, nothing to get."
        )

    if not matcha_state_service.state_exists():
        # if the state file doesn't exist, then download it from the remote
        remote_state.download(os.getcwd())

        # reinitialise to create the necessary variables
        matcha_state_service = MatchaStateService()

    with remote_state.use_lock():
        local_hash = matcha_state_service.get_hash_local_state()
        remote_hash = remote_state.get_hash_remote_state(
            matcha_state_service.matcha_state_path
        )

        if local_hash != remote_hash:
            remote_state.download(os.getcwd())

            matcha_state_service = MatchaStateService()

        if resource_name:
            get_command_validation(
                resource_name,
                matcha_state_service.get_resource_names(),
                "resource type",
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


def analytics_opt_out() -> None:
    """Disable the collection of anonymous usage data."""
    GlobalParameters().analytics_opt_out = True


def analytics_opt_in() -> None:
    """Enable the collection of anonymous usage data (enabled by default)."""
    GlobalParameters().analytics_opt_out = False


def remove_state_lock() -> None:
    """Unlock remote state."""
    remote_state = RemoteStateManager()
    remote_state.unlock()


@track(event_name=AnalyticsEvent.PROVISION)
def provision(
    location: str,
    prefix: str,
    password: str,
    verbose: Optional[bool] = False,
) -> MatchaState:
    """Provision cloud resources using templates.

    Args:
        location (str): Azure location in which all resources will be provisioned.
        prefix (str): Prefix used for all resources.
        password (str): Password for ZenServer.
        verbose (bool optional): additional output is show when True. Defaults to False.

    Returns:
        MatchaState: the information of the provisioned resources.

    Raises:
        MatchaError: If resources are already provisioned.
        MatchaError: If prefix is not valid.
        MatchaError: If region is not valid.
    """
    remote_state_manager = RemoteStateManager()

    if remote_state_manager.is_state_stale():
        if verbose:
            print_status(
                build_warning_status(
                    "Matcha has detected a stale state file. This means that your local configuration is out of sync with the remote state, the resource group may have been removed. Deleting existing state config."
                )
            )
        remote_state_manager.remove_matcha_config()

    if remote_state_manager.is_state_provisioned():
        raise MatchaError(
            "Error - Matcha has detected that there are resources already provisioned. Use 'matcha destroy' to remove the existing resources before trying to provision again."
        )

    # Input variable checks
    try:
        prefix = prefix.lower()
        _ = is_valid_prefix(prefix)
        _ = is_valid_region(location)
    except MatchaInputError as e:
        raise e

    # Provision resource group and remote state storage
    remote_state_manager.provision_remote_state(location, prefix)

    with remote_state_manager.use_lock(), remote_state_manager.use_remote_state():
        # create a runner for provisioning resource with Terraform service.
        template_runner = AzureRunner()

        project_directory = os.getcwd()
        destination = os.path.join(
            project_directory, ".matcha", "infrastructure", "resources"
        )
        template = os.path.join(
            os.path.dirname(__file__), os.pardir, "infrastructure", "resources"
        )

        azure_template = AzureTemplate()

        config = azure_template.build_template_configuration(
            location=location, prefix=prefix, password=password
        )
        azure_template.build_template(config, template, destination, verbose)

        template_runner.provision()

        matcha_state_service = MatchaStateService()

        return matcha_state_service.fetch_resources_from_state_file()
