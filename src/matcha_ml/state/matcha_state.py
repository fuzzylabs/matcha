"""The matcha state interface."""
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from matcha_ml.constants import MATCHA_STATE_PATH


@dataclass
class MatchaResource:
    """A class to represent a resource in the state."""

    name: str


@dataclass
class MatchaResourceProperty:
    """A class to represent a resource property in the state."""

    name: str
    value: str


@dataclass
class MatchaStateComponent:
    """A class to represent a component in the state."""

    resource: MatchaResource
    properties: List[MatchaResourceProperty]


@dataclass
class MatchaState:
    """A class to represent the state as a whole."""

    components: List[MatchaStateComponent]

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Convert the MatchaState object to a dictionary.

        Used for integration with legacy code - will be removed.

        Returns:
            Dict[str, Dict[str, str]]: the MatchaState as a dictionary.
        """
        state_dictionary = {}
        for component in self.components:
            state_dictionary[component.resource.name] = {
                property.name: property.value for property in component.properties
            }

        return state_dictionary


class MatchaStateService:
    """A matcha state service for handling to matcha.state file."""

    matcha_state_path = MATCHA_STATE_PATH

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
        return bool(os.path.isfile(cls.matcha_state_path))

    @property
    def state_file(self) -> Dict[str, Dict[str, str]]:
        """Getter of the state file.

        Returns:
            Dict[str, Dict[str, str]]: the state file in the format of a dictionary.
        """
        with open(self.matcha_state_path) as f:
            self._state = dict(json.load(f))
            return dict(self._state)

    def _convert_to_matcha_state_object(
        self, state_dict: Dict[str, Dict[str, str]]
    ) -> MatchaState:
        """An internal function to convert a dictionary representation of the state file to an object version.

        Args:
            state_dict (Dict[str, Dict[str, str]]): the raw state file as a dictionary.

        Returns:
            MatchaState: the state file in it's object form.
        """
        state_components: List[MatchaStateComponent] = []
        for resource, properties in state_dict.items():
            state_components.append(
                MatchaStateComponent(
                    resource=MatchaResource(name=resource),
                    properties=[
                        MatchaResourceProperty(name=key, value=value)
                        for key, value in properties.items()
                    ],
                )
            )

        return MatchaState(components=state_components)

    def fetch_resources_from_state_file(
        self,
        resource_name: Optional[str] = None,
        property_name: Optional[str] = None,
    ) -> MatchaState:
        """Either return all of the resources or resource specified by the resource name.

        Args:
            resource_name (Optional[str]): the name of the resource to get. Defaults to None.
            property_name (Optional[str]): the property to get from the specified resource. Defaults to None.

        Returns:
            MatchaState: the state.
        """
        if resource_name is None:
            return self._convert_to_matcha_state_object(self._state)

        if property_name is None:
            return self._convert_to_matcha_state_object(
                {str(resource_name): dict(self._state[resource_name])}
            )

        property_value = self._state.get(resource_name, {})[property_name]

        return self._convert_to_matcha_state_object(
            {resource_name: {property_name: property_value}}
        )

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

    def get_hash_local_state(self) -> str:
        """Get hash of the local matcha state file.

        Returns:
            str: Hash contents of the blob in hexadecimal string
        """
        local_hash = None
        with open(self.matcha_state_path, "rb") as fp:
            local_hash = hashlib.md5(fp.read()).hexdigest()
        return local_hash
