"""The matcha state interface."""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from matcha_ml.constants import MATCHA_STATE_PATH
from matcha_ml.errors import MatchaError

MISSING_STATE_ERROR_MSG = "No state file exists, you need to 'provision' resources or 'get' from already provisioned resources."


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

    def find_property(self, property_name: str) -> MatchaResourceProperty:
        """Given a property name, find the property that matches it.

        Note: this is works under the assumption of none-duplicated properties.

        Args:
            property_name (str): the name of the property.

        Raises:
            MatchaError: if the property could not be found.

        Returns:
            MatchaResourceProperty: the property that matches the property_name parameter.
        """
        property = next(
            filter(lambda property: property.name == property_name, self.properties),
            None,
        )

        if property is None:
            raise MatchaError(
                f"The property with the name '{property_name}' could not be found."
            )

        return property


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

    @staticmethod
    def from_dict(state_dict: Dict[str, Dict[str, str]]) -> MatchaState:
        """A function to convert a dictionary representation of state to a MatchaState instance.

        Args:
            state_dict (Dict[str, Dict[str, str]]): the dictionary representation of state.

        Returns:
            MatchaState: the MatchaState representation of state.
        """
        components: List[MatchaStateComponent] = []
        for resource, properties in state_dict.items():
            components.append(
                MatchaStateComponent(
                    resource=MatchaResource(name=resource),
                    properties=[
                        MatchaResourceProperty(name=key, value=value)
                        for key, value in properties.items()
                    ],
                )
            )

        return MatchaState(components=components)


class MatchaStateService:
    """A matcha state service for handling to matcha.state file."""

    matcha_state_path = MATCHA_STATE_PATH

    def __init__(self) -> None:
        """Constructor for the MatchaStateService.

        Raises:
            MatchaError: if the state file does not exist.
        """
        if self.state_exists():
            self._state = self._read_state()
        else:
            raise MatchaError(MISSING_STATE_ERROR_MSG)

    @classmethod
    def state_exists(cls) -> bool:
        """Check if state file exists.

        Returns:
            bool: returns True if exists, otherwise False.
        """
        return bool(os.path.isfile(cls.matcha_state_path))

    def _read_state(self) -> MatchaState:
        """Read the state from the local file system.

        Raises:
            MatchaError: if the state doesn't exist locally.

        Returns:
            MatchaState: the state for the provisioned resources.
        """
        if not self.state_exists():
            raise MatchaError(MISSING_STATE_ERROR_MSG)

        with open(self.matcha_state_path) as in_file:
            self._state = MatchaState.from_dict(json.load(in_file))
        return self._state

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
            return self._state

        if property_name is None:
            return MatchaState(
                components=[self.get_component(resource_name=resource_name)]
            )

        component = self.get_component(resource_name=resource_name)
        property = component.find_property(property_name=property_name)

        return MatchaState(
            components=[
                MatchaStateComponent(resource=component.resource, properties=[property])
            ]
        )

    def get_component(self, resource_name: str) -> MatchaStateComponent:
        """Get a component of the state given a resource name.

        Args:
            resource_name (str): the components resource name

        Raises:
            MatchaError: if the component cannot be found in the state.

        Returns:
            MatchaStateComponent: the state component matching the resource name parameter.
        """
        component = next(
            filter(
                lambda component: component.resource.name == resource_name,
                self._state.components,
            ),
            None,
        )

        if component is None:
            raise MatchaError(
                f"The component with the name '{resource_name}' could not be found in the state."
            )

        return component

    def get_resource_names(self) -> List[str]:
        """Method for returning all existing resource names.

        Returns:
            List[str]: a list of existing resource names.
        """
        return [component.resource.name for component in self._state.components]

    def get_property_names(self, resource_name: str) -> List[str]:
        """Method for returning all existing properties for a given resource.

        Args:
            resource_name (str): the resource name to get properties from.

        Returns:
            List[str]: a list of existing properties for a given resource.
        """
        return [
            property.name
            for component in self._state.components
            for property in component.properties
            if component.resource.name == resource_name
        ]

    def get_hash_local_state(self) -> str:
        """Get hash of the local matcha state file.

        Returns:
            str: Hash contents of the blob in hexadecimal string
        """
        local_hash = None
        with open(self.matcha_state_path, "rb") as fp:
            local_hash = hashlib.md5(fp.read()).hexdigest()
        return local_hash
