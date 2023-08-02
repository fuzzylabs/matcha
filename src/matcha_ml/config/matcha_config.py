"""The matcha.config.json file interface."""
import json
import os
from dataclasses import dataclass
from typing import Dict, List

from matcha_ml.errors import MatchaError

MISSING_CONFIG_ERROR_MSG = "No config file exists, you need to 'provision' resources or use an existing 'matcha.config.json' file from already provisioned resources to take advantage of shared state."


@dataclass
class MatchaConfigComponentProperty:
    """docstring."""

    name: str
    value: str


@dataclass
class MatchaConfigComponent:
    """docstring."""

    name: str
    properties: List[MatchaConfigComponentProperty]

    def find_property(self, property_name: str) -> MatchaConfigComponentProperty:
        """Given a property name, find the property that matches it.

        Note: this only works under the assumption of none-duplicated properties.

        Args:
            property_name (str): the name of the property.

        Raises:
            MatchaError: if the property could not be found.

        Returns:
            MatchaConfigComponentProperty: the property that matches the property_name parameter.
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
class MatchaConfig:
    """docstring."""

    components: List[MatchaConfigComponent]

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Convert the MatchaConfig object to a dictionary.

        Returns:
            Dict[str, Dict[str, str]]: the MatchaState as a dictionary.
        """
        state_dictionary = {}
        for config_component in self.components:
            state_dictionary[config_component.name] = {
                property.name: property.value
                for property in config_component.properties
            }

        return state_dictionary

    @staticmethod
    def from_dict(state_dict: Dict[str, Dict[str, str]]) -> MatchaConfig:
        """A function to convert a dictionary representation of state to a MatchaState instance.

        Args:
            state_dict (Dict[str, Dict[str, str]]): the dictionary representation of state.

        Returns:
            MatchaConfig: the MatchaConfig representation of the config json.
        """
        components: List[MatchaConfigComponent] = []
        for resource, properties in state_dict.items():
            components.append(
                MatchaConfigComponent(
                    name=resource,
                    properties=[
                        MatchaConfigComponentProperty(name=key, value=value)
                        for key, value in properties.items()
                    ],
                )
            )

        return MatchaConfig(components=components)


class MatchaConfigService:
    """docstring."""

    @staticmethod
    def read_matcha_config() -> MatchaConfig:
        """docstring."""
        local_config_file = os.path.join(os.getcwd(), "matcha.config.json")

        if os.path.exists(local_config_file):
            with open(local_config_file) as config:
                local_config = json.load(config)

        return MatchaConfig.from_dict(local_config)

    @staticmethod
    def delete_matcha_config() -> None:
        """docstring."""
        local_config_file = os.path.join(os.getcwd(), "matcha.config.json")

        try:
            os.remove(local_config_file)
        except Exception:
            raise MatchaError(
                f"Local config file at path:{local_config_file} could not be removed."
            )
