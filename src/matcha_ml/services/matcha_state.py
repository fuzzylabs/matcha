"""The matcha state interface."""
import json
import os
from typing import Dict, List, Optional


class MatchaStateService:
    """A matcha state service for handling to matcha.state file."""

    def __init__(self) -> None:
        """A constructor for the service which loads the state file."""
        if os.path.isfile(".matcha/infrastructure/matcha.state"):
            with open(".matcha/infrastructure/matcha.state") as f:
                self._state = dict(json.load(f))

    @property
    def state_file(self) -> Dict[str, str]:
        """Getter of the state file.

        Returns:
            Dict[str, str]: the state file in the format of a dictionary.
        """
        return dict(self._state)

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
