"""Run terraform templates to provision and deprovision resources."""
import json
import os
import shutil

from matcha_ml.cli.ui.print_messages import (
    print_json,
    print_status,
)
from matcha_ml.cli.ui.resource_message_builders import (
    dict_to_json,
    hide_sensitive_in_output,
)
from matcha_ml.cli.ui.status_message_builders import (
    build_status,
)
from matcha_ml.runners.base_runner import BaseRunner
from matcha_ml.state.matcha_state import MatchaState, MatchaStateService

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

    def _show_terraform_outputs(self, matcha_state: MatchaState) -> None:
        """Print the formatted Terraform outputs.

        Args:
            matcha_state (MatchaState): Terraform outputs in a MatchaState format.
        """
        print_status(build_status("Here are the endpoints for what's been provisioned"))
        resources_dict = hide_sensitive_in_output(matcha_state.to_dict())
        resources_json = dict_to_json(resources_dict)
        print_json(resources_json)

    def is_local_state_stale(self) -> bool:
        """Checks for congruence between the local config file and the local tfvars file."""
        local_tfvars_file = os.path.join(
            os.getcwd(),
            ".matcha",
            "infrastructure",
            "remote_state_storage",
            "terraform.tfvars.json",
        )
        local_config_file = os.path.join(os.getcwd(), "matcha.config.json")
        if os.path.exists(local_tfvars_file) and os.path.exists(local_config_file):
            with open(local_tfvars_file) as tf:
                local_tfvars = json.load(tf)
            with open(local_config_file) as config:
                local_config = json.load(config)
                index = local_config["remote_state_bucket"]["resource_group_name"].find(
                    "-"
                )
                local_config["prefix"] = local_config["remote_state_bucket"][
                    "resource_group_name"
                ][:index]
            return bool(local_config["prefix"] != local_tfvars["prefix"])
        else:
            return False

    def remove_matcha_dir(self) -> None:
        """Removes the project's .matcha directory"."""
        project_directory = os.getcwd()
        target = os.path.join(project_directory, ".matcha")
        if os.path.exists(target):
            shutil.rmtree(target)

    def provision(self) -> None:
        """Provision resources required for the deployment."""
        self._check_terraform_installation()
        self._validate_terraform_config()
        self._validate_kubeconfig(base_path=".kube/config")
        self._initialize_terraform(msg="Matcha")
        self._apply_terraform()
        tf_output = self.tfs.terraform_client.output()
        matcha_state_service = MatchaStateService(terraform_output=tf_output)
        self._show_terraform_outputs(matcha_state_service._state)

    def deprovision(self) -> None:
        """Destroy the provisioned resources."""
        self._check_matcha_directory_exists()
        self._check_terraform_installation()
        self._initialize_terraform(msg="Matcha", destroy=True)
        self._destroy_terraform(msg="Matcha")
