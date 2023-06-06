"""The core functions for matcha."""
import os
from typing import Dict, Optional

from matcha_ml.cli._validation import get_command_validation
from matcha_ml.errors import MatchaError
from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.state import MatchaStateService, RemoteStateManager


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

    if not matcha_state_service.state_file_exists:
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
