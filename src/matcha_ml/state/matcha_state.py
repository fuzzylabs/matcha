"""The matcha state interface."""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from matcha_ml.constants import MATCHA_STATE_PATH
from matcha_ml.errors import MatchaError, MatchaInputError

MISSING_STATE_ERROR_MSG = "No state file exists, you need to 'provision' resources or 'get' from already provisioned resources."

RESOURCE_NAMES = [
    "experiment_tracker",
    "pipeline",
    "orchestrator",
    "cloud",
    "container_registry",
    "model_deployer",
    "data_version_control",
]


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

        Note: this only works under the assumption of none-duplicated properties.

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

    def __init__(
        self,
        matcha_state: Optional[MatchaState] = None,
        terraform_output: Optional[Dict[str, str]] = None,
    ) -> None:
        """Constructor for the MatchaStateService.

        Note: this object should not be initialized with both 'matcha_state' and 'terraform_output' arguments.

        Args:
            matcha_state (Optional[MatchaState]): MatchaState object to initialize the service with. Defaults to None.
            terraform_output (Optional[dict]): Output from Terraform to be parsed into a MatchaState object on initialization. Defaults to None.

        Raises:
            MatchaError: if the state file does not exist.
            MatchaError: if MatchaStateService is initialized with both 'matcha_state' and 'terraform_output' arguments.
        """
        if matcha_state is not None and terraform_output is not None:
            raise MatchaError(
                "MatchaStateService constructor cannot be called with both 'matcha_state' and 'terraform_output' arguments."
            )

        if matcha_state is not None:
            self._state = matcha_state
            self._write_state(matcha_state=matcha_state)
        elif terraform_output is not None:
            self._state = self.build_state_from_terraform_output(terraform_output)
            self._write_state(self._state)
        elif self.state_exists():
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

    def build_state_from_terraform_output(
        self, terraform_output: Dict[str, str]
    ) -> MatchaState:
        """Builds a MatchaState class from a terraform output dictionary.

        Args:
            terraform_output (Dict[str, str]): Terraform output variables as a dictionary

        Returns:
            MatchaState: Terraform output variables in a MatchaState dataclass format.
        """

        def _parse_terraform_output_resource_name(
            output_name: str,
        ) -> Tuple[str, str, str]:
            """Build resource output for each Terraform output.

            Format for Terraform output names is:
            <resource>_<flavor>_<property>
            where <resource> is a name found in RESOURCE_NAMES

            Args:
                output_name (str): the name of the Terraform output.

            Returns:
                Tuple[str, str, str]: the resource output for matcha.state.
            """
            resource_type: Optional[str] = None

            for key in RESOURCE_NAMES:
                if key in output_name:
                    resource_type = key
                    break

            if resource_type is None:
                raise MatchaInputError(
                    f"A valid resource type for the output '{output_name}' does not exist."
                )

            flavor_and_resource_name = output_name[len(resource_type) + 1 :]

            flavor, resource_name = flavor_and_resource_name.split("_", maxsplit=1)
            resource_name = resource_name.replace("_", "-")
            resource_type = resource_type.replace("_", "-")

            return resource_type, flavor, resource_name

        state_outputs: Dict[str, Dict[str, str]] = defaultdict(dict)

        for output_name, properties in terraform_output.items():
            (
                resource_type,
                flavor,
                resource_name,
            ) = _parse_terraform_output_resource_name(output_name)
            state_outputs[resource_type].setdefault("flavor", flavor)
            state_outputs[resource_type][resource_name] = properties["value"]  # type: ignore

        # Create a unique matcha state identifier
        state_outputs["id"] = {"matcha_uuid": str(uuid.uuid4())}

        return MatchaState.from_dict(state_outputs)

    def _write_state(self, matcha_state: MatchaState) -> None:
        """Writes a given MatchaState object to the matcha.state file.

        Args:
            matcha_state (MatchaState): State dataclass object to be written to the state file.
        """
        with open(self.matcha_state_path, "w") as f:
            json.dump(matcha_state.to_dict(), f, indent=4)

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

    def is_local_state_stale(self) -> bool:
        """Checks for congruence between the local config file and the local state file."""
        local_config_file = os.path.join(os.getcwd(), "matcha.config.json")

        # the resource group name from the state object
        matcha_state_resource_group = (
            self.get_component("cloud").find_property("resource-group-name").value
        )

        if self.state_exists() and os.path.exists(local_config_file):
            with open(local_config_file) as config:
                local_config = json.load(config)

            return bool(
                matcha_state_resource_group
                != local_config["remote_state_bucket"]["resource_group_name"]
            )
        else:
            return False

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
