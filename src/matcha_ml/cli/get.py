"""Get CLI consists of ."""
from typing import Dict, Optional

from matcha_ml.services.matcha_state import MatchaStateService


def get_resources(
    resource_name: Optional[str],
    property_name: Optional[str],
    matcha_state_service: MatchaStateService,
) -> Dict[str, Dict[str, str]]:
    """Return the information of the provisioned resource based on the resource name specified.

    Return all resources if no resource name is specified.

    Args:
        resource_name (Optional[str]): name of the resource to get information for.
        property_name (Optional[str]): the property of the resource to get.
        matcha_state_service (MatchaStateService): the matcha state service for interacting with the matcha.state file.

    Returns:
        Dict[str, Dict[str, str]]: the information of the provisioned resource.
    """
    result = matcha_state_service.fetch_resources_from_state_file(
        resource_name, property_name
    )
    return result
