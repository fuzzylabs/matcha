"""The core functions for matcha."""
import os
from typing import Dict, Optional

from matcha_ml.cli._validation import get_command_validation
from matcha_ml.errors import MatchaError
from matcha_ml.services.matcha_state import MatchaStateService


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
