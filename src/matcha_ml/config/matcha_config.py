"""The matcha.config.json file interface."""
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from matcha_ml.errors import MatchaError

DEFAULT_CONFIG_NAME = "matcha.config.json"


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

    def find_component(self, component_name: str) -> MatchaConfigComponent:
        """Given a component name, find the component that matches it.

        Note: this only works under the assumption of none-duplicated properties.

        Args:
            component_name (str): the name of the component.

        Raises:
            MatchaError: if the component could not be found.

        Returns:
            MatchaConfigComponent: the component that matches the component_name parameter.
        """
        component = next(
            filter(lambda component: component.name == component_name, self.components),
            None,
        )

        if component is None:
            raise MatchaError(
                f"The component with the name '{component_name}' could not be found."
            )

        return component

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
    def from_dict(state_dict: Dict[str, Dict[str, str]]) -> "MatchaConfig":
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
    def get_stack() -> Optional[MatchaConfigComponentProperty]:
        """Gets the current stack name from the Matcha Config if it exists.

        Returns:
            Optional[MatchaConfigComponentProperty]: The name of the current stack being used as a config component object.
        """
        try:
            stack = (
                MatchaConfigService.read_matcha_config()
                .find_component("stack")
                .find_property("name")
            )
        except MatchaError:
            stack = None

        return stack

    @staticmethod
    def write_matcha_config(matcha_config: MatchaConfig) -> None:
        """A function for writing the local Matcha config file.

        Args:
            matcha_config (MatchaConfig): the MatchaConfig representation of the MatchaConfig instance.
        """
        local_config_file = os.path.join(os.getcwd(), DEFAULT_CONFIG_NAME)

        with open(local_config_file, "w") as file:
            json.dump(matcha_config.to_dict(), file)

    @staticmethod
    def read_matcha_config() -> MatchaConfig:
        """A function for reading the Matcha config file into a MatchaConfig object.

        Returns:
           MatchaConfig: the MatchaConfig representation of the MatchaConfig instance.

        Raises:
            MatchaError: raises a MatchaError if the local config file could not be read.
        """
        local_config_file = os.path.join(os.getcwd(), DEFAULT_CONFIG_NAME)

        if os.path.exists(local_config_file):
            with open(local_config_file) as config:
                local_config = json.load(config)

            return MatchaConfig.from_dict(local_config)
        else:
            raise MatchaError(
                f"No '{DEFAULT_CONFIG_NAME}' file found, please generate one by running 'matcha provision', or add an existing ''{DEFAULT_CONFIG_NAME}'' file to the root project directory."
            )

    @staticmethod
    def config_file_exists() -> bool:
        """A convencience function which checks for the existence of the matcha.config.json file.

        Returns:
            True if the matcha.config.json file exists, False otherwise.
        """
        return os.path.exists(os.path.join(os.getcwd(), DEFAULT_CONFIG_NAME))

    @staticmethod
    def update(
        components: Union[MatchaConfigComponent, List[MatchaConfigComponent]]
    ) -> None:
        """A function which updates the matcha config file.

        If no config file exists, this function will create one.

        Args:
            components (dict): A list of, or single MatchaConfigComponent object(s).
        """
        if isinstance(components, MatchaConfigComponent):
            components = [components]

        if MatchaConfigService.config_file_exists():
            config = MatchaConfigService.read_matcha_config()
            config.components += components
        else:
            config = MatchaConfig(components)

        MatchaConfigService.write_matcha_config(config)

    @staticmethod
    def delete_matcha_config() -> None:
        """A function for deleting the local Matcha config file.

        Raises:
            MatchaError: raises a MatchaError if the local config file could not be removed.
        """
        local_config_file = os.path.join(os.getcwd(), DEFAULT_CONFIG_NAME)

        try:
            os.remove(local_config_file)
        except Exception:
            raise MatchaError(
                f"Local config file at path:{local_config_file} could not be removed."
            )
