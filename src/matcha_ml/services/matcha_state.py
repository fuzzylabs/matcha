"""The matcha state interface."""
import json
import os
from typing import Dict, Optional

MATCHA_STATE_DIR = os.path.join(".matcha", "infrastructure", "matcha.state")


class MatchaStateService:
    """A matcha state service for handling to matcha.state file."""

    _state: Optional[Dict[str, Dict[str, str]]] = None

    def check_state_file_exists(self) -> bool:
        """Check if state file exists.

        Returns:
            bool: returns True if exists, otherwise False.
        """
        if os.path.isfile(MATCHA_STATE_DIR):
            self._state = self._state_file
            return True
        else:
            return False

    @property
    def _state_file(self) -> Dict[str, Dict[str, str]]:
        """Getter of the state file.

        Returns:
            Dict[str, Dict[str, str]]: the state file in the format of a dictionary.
        """
        with open(MATCHA_STATE_DIR) as f:
            self._state = dict(json.load(f))
            return dict(self._state)

    def fetch_resources_from_state_file(
        self,
        resource_name: Optional[str] = None,
        property_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Either return all of the resources or resource specified by the resource name.

        Args:
            resource_name (Optional[str]): the name of the resource to get. Defaults to None.
            property_name (Optional[str]): the property to get from the specified resource. Defaults to None.

        Returns:
            Dict[str, Dict[str, str]]: resources in the format of a dictionary.
        """
        if resource_name is None:
            return self._state
        elif resource_name and property_name is None:
            return {str(resource_name): dict(self._state.get(resource_name))}
        else:
            property_value = str(self._state.get(resource_name).get(property_name))
            return {resource_name: {property_name: property_value}}
