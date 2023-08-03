"""The matcha.config.json file interface."""
import json
import os
from dataclasses import dataclass
from typing import Dict, List

from matcha_ml.errors import MatchaError


@dataclass
class MatchaConfigComponentProperty:
    """A class to represent Matcha config properties."""

    name: str
    value: str


@dataclass
class MatchaConfigComponent:
    """A class to represent Matcha config components."""

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
    """A class to represent the Matcha config file."""

    components: List[MatchaConfigComponent]

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """A function to convert the MatchaConfig class into a dictionary.

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
        """A function to convert a dictionary representation of the Matcha config file into a MatchaConfig instance.

        Args:
            state_dict (Dict[str, Dict[str, str]]): the dictionary representation of the Matcha config file.

        Returns:
            MatchaConfig: the MatchaConfig representation of the MatchaConfig instance.
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
    """A service for handling the Matcha config file."""

    @staticmethod
    def read_matcha_config() -> MatchaConfig:
        """A function for reading the Matcha config file into a MatchaConfig object.

        Returns:
           MatchaConfig: the MatchaConfig representation of the MatchaConfig instance.
        """
        local_config_file = os.path.join(os.getcwd(), "matcha.config.json")

        if os.path.exists(local_config_file):
            with open(local_config_file) as config:
                local_config = json.load(config)

        return MatchaConfig.from_dict(local_config)

    @staticmethod
    def delete_matcha_config() -> None:
        """A function for deleting the local Matcha config file.

        Raises:
        MatchaError: raises a MatchaError if the local config file could not be removed.
        """
        local_config_file = os.path.join(os.getcwd(), "matcha.config.json")

        try:
            os.remove(local_config_file)
        except Exception:
            raise MatchaError(
                f"Local config file at path:{local_config_file} could not be removed."
            )
