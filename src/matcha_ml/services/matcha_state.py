"""The matcha state interface."""
import json
import os
from typing import Dict, List, Optional

MATCHA_STATE_DIR = os.path.join(".matcha", "infrastructure", "matcha.state")


class MatchaStateService:
    """A matcha state service for handling to matcha.state file."""

    state_file_exists = False
    _state: Optional[Dict[str, str]] = None

    def __init__(self) -> None:
        """A constructor for the service which loads the state file."""
        self.state_file_exists = self.check_state_file_exists()
        self._state = self.state_file

    def check_state_file_exists(self) -> bool:
        """Check if state file exists.

        Returns:
            bool: returns True if exists, otherwise False.
        """
        return bool(os.path.isfile(MATCHA_STATE_DIR))

    @property
    def state_file(self) -> Dict[str, str]:
        """Getter of the state file.

        Returns:
            Dict[str, str]: the state file in the format of a dictionary.
        """
        if self.state_file_exists:
            with open(MATCHA_STATE_DIR) as f:
                self._state = dict(json.load(f))
                return dict(self._state)
        else:
            print("Error, matcha.state does not exists")

    def fetch_resources_from_state_file(
        self, resource_names: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Either return all of the resources or resource specified by the resource name.

        Args:
            resource_names (Optional[List[str]], optional): the name of the resource to get. Defaults to None.

        Returns:
            Dict[str, str]: resources in the format of a dictionary.
        """
        if resource_names is None:
            return dict(self._state)
        else:
            return {
                str(resource_name): str(self._state.get(resource_name))
                for resource_name in resource_names
            }
