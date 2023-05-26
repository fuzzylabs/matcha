"""Run terraform templates to provision and deprovision resources."""
import json
import uuid
from collections import defaultdict
from typing import Dict, Tuple

from matcha_ml.cli.ui.print_messages import (
    print_error,
    print_json,
    print_status,
)
from matcha_ml.cli.ui.resource_message_builders import (
    dict_to_json,
    hide_sensitive_in_output,
)
from matcha_ml.cli.ui.status_message_builders import build_status
from matcha_ml.errors import MatchaInputError
from matcha_ml.runners.base_runner import BaseRunner

RESOURCE_NAMES = [
    "experiment_tracker",
    "pipeline",
    "orchestrator",
    "cloud",
    "container_registry",
    "model_deployer",
]


class AzureRunner(BaseRunner):
    """A Runner class provides methods that interface with the Terraform service to facilitate the provisioning and deprovisioning of resources."""

    def __init__(self) -> None:
        """Initialize AzureRunner class."""
        super().__init__()

    def _build_resource_output(self, output_name: str) -> Tuple[str, str, str]:
        """Build resource output for each Terraform output.

        Args:
            output_name (str): the name of the Terraform output.

        Returns:
            Tuple[str, str, str]: the resource output for matcha.state.
        """
        resource_type: str

        for key in RESOURCE_NAMES:
            if key in output_name:
                resource_type = key
                break

        if resource_type is None:
            print_error(
                "A valid resource type for the output '{output_name}' does not exist."
            )
            raise MatchaInputError()

        flavour_and_resource_name = output_name[len(resource_type) + 1 :]

        flavor, resource_name = flavour_and_resource_name.split("_", maxsplit=1)
        resource_name = resource_name.replace("_", "-")
        resource_type = resource_type.replace("_", "-")

        return resource_type, flavor, resource_name

    def _write_outputs_state(self) -> None:
        """Write the outputs of the Terraform deployment to the state JSON file."""
        tf_outputs = self.tfs.terraform_client.output()
        state_outputs: Dict[str, Dict[str, str]] = defaultdict(dict)

        for output_name, properties in tf_outputs.items():
            resource_type, flavor, resource_name = self._build_resource_output(
                output_name
            )
            state_outputs[resource_type].setdefault("flavor", flavor)
            state_outputs[resource_type][resource_name] = properties["value"]

        # Create a unique matcha state identifier
        state_outputs["id"] = {"matcha_uuid": str(uuid.uuid4())}

        self._update_state_file(state_outputs)

    def _update_state_file(self, state_outputs: Dict[str, Dict[str, str]]) -> None:
        """Read and update the matcha state file with new provisioned resources.

        Args:
            state_outputs (Dict[str, Dict[str, str]]): Dictionary containing outputs to be written to state file.
        """
        with open(self.state_file) as f:
            current_data = json.load(f)
        state_outputs["cloud"].update(current_data["cloud"])
        with open(self.state_file, "w") as f:
            json.dump(state_outputs, f, indent=4)

    def _show_terraform_outputs(self) -> None:
        """Print the terraform outputs from state file."""
        self._write_outputs_state()
        print_status(build_status("Here are the endpoints for what's been provisioned"))
        # print terraform output from state file
        with open(self.state_file) as fp:
            resources_dict = hide_sensitive_in_output(json.loads(fp.read()))
            resources_json = dict_to_json(resources_dict)
            print_json(resources_json)

    def provision(self) -> None:
        """Provision resources required for the deployment."""
        self._check_terraform_installation()
        self._validate_terraform_config()
        self._validate_kubeconfig(base_path=".kube/config")
        self._initialize_terraform(msg="Matcha")
        self._apply_terraform()
        self._show_terraform_outputs()

    def deprovision(self) -> None:
        """Destroy the provisioned resources."""
        self._check_matcha_directory_exists()
        self._check_terraform_installation()
        self._destroy_terraform(msg="Matcha")
