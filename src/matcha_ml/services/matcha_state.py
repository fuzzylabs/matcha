"""The matcha state interface."""
import json
import os
from typing import Dict, List, Optional


class MatchaStateService:
    """A matcha state service for handling to matcha.state file."""

    matcha_state_dir = os.path.join(".matcha", "infrastructure", "matcha.state")

    def __init__(self) -> None:
        """MatchaStateService constructor."""
        self.state_file_exists = self.check_state_file_exists()
        if self.state_file_exists:
            self._state = self.state_file

    @classmethod
    def check_state_file_exists(cls) -> bool:
        """Check if state file exists.

        Returns:
            bool: returns True if exists, otherwise False.
        """
        return bool(os.path.isfile(cls.matcha_state_dir))

    @property
    def state_file(self) -> Dict[str, Dict[str, str]]:
        """Getter of the state file.

        Returns:
            Dict[str, Dict[str, str]]: the state file in the format of a dictionary.
        """
        with open(self.matcha_state_dir) as f:
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

        if property_name is None:
            return {str(resource_name): dict(self._state[resource_name])}

        property_value = self._state.get(resource_name, {})[property_name]

        return {resource_name: {property_name: property_value}}

    def get_resource_names(self) -> List[str]:
        """Method for returning all existing resource names.

        Returns:
            List[str]: a list of existing resource names.
        """
        return list(self._state.keys())

    def get_property_names(self, resource_name: str) -> List[str]:
        """Method for returning all existing properties for a given resource.

        Args:
            resource_name (str): the resource name to get properties from.

        Returns:
            List[str]: a list of existing properties for a given resource.
        """
        return list(self._state.get(resource_name, {}).keys())
