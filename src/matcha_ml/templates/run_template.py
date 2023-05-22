"""Run terraform templates to provision and deprovision resources."""
import json
import os
from collections import defaultdict
from typing import Dict, Tuple

import typer

from matcha_ml.cli.ui.emojis import Emojis
from matcha_ml.cli.ui.print_messages import (
    print_error,
    print_json,
    print_status,
)
from matcha_ml.cli.ui.resource_message_builders import (
    dict_to_json,
    hide_sensitive_in_output,
)
from matcha_ml.cli.ui.spinner import Spinner
from matcha_ml.cli.ui.status_message_builders import (
    build_resource_confirmation,
    build_status,
    build_substep_success_status,
)
from matcha_ml.errors import MatchaInputError, MatchaTerraformError
from matcha_ml.services.terraform_service import TerraformService

SPINNER = "dots"

RESOURCE_NAMES = [
    "experiment_tracker",
    "pipeline",
    "orchestrator",
    "cloud",
    "container_registry",
    "model_deployer",
]


class TemplateRunner:
    """A Runner class provides methods that interface with the Terraform service to facilitate the provisioning and deprovisioning of resources."""

    tfs: TerraformService = TerraformService()
    tf_state_dir = tfs.get_tf_state_dir()
    state_file = tfs.config.state_file

    def _check_terraform_installation(self) -> None:
        """Checks if terraform is installed on the host system.

        Raises:
            typer.Exit: if terraform is not installed.
        """
        if not self.tfs.check_installation():
            print_error(f"{Emojis.CROSS.value} Terraform is not installed")
            print_error(
                "Terraform is required for to run and was not found installed on your machine. "
                "Please visit https://learn.hashicorp.com/tutorials/terraform/install-cli to install it."
            )
            raise typer.Exit()

    def _validate_terraform_config(self) -> None:
        """Validate the configuration used for creating resources.

        Raises:
            typer.Exit: if `terraform.tfvars.json` file not found in current directory.
        """
        if not self.tfs.validate_config():
            print_error(
                "The file terraform.tfvars.json was not found in the "
                f"current directory at {self.tfs.config.var_file}. Please "
                "verify if it exists."
            )
            raise typer.Exit()

    def _validate_kubeconfig(self, base_path: str = ".kube/config") -> None:
        """Check if kubeconfig file exists at location '~/.kube/config', if not create empty config file.

        Args:
            base_path (str): Relative path to location of kubeconfig
        """
        self.tfs.verify_kubectl_config_file(base_path)

    def _initialize_terraform(self) -> None:
        """Run terraform init to initialize Terraform .

        Raises:
            MatchaTerraformError: if 'terraform init' failed.
        """
        if self.tf_state_dir.exists():
            # this directory gets created after a successful init command
            print_status(
                build_status(
                    f"matcha {Emojis.MATCHA.value} has already been initialized. Skipping this step..."
                )
            )

        else:
            print_status(
                build_status(
                    f"\n{Emojis.WAITING.value} Brewing matcha {Emojis.MATCHA.value}...\n"
                )
            )

            with Spinner("Initializing"):
                ret_code, _, err = self.tfs.init()

                if ret_code != 0:
                    print_error("The command 'terraform init' failed.")
                    raise MatchaTerraformError(tf_error=err)

            print_status(
                build_substep_success_status(
                    f"{Emojis.CHECKMARK.value} Matcha {Emojis.MATCHA.value} initialized!\n"
                )
            )

    def _check_matcha_directory_exists(self) -> None:
        """Checks if .matcha directory exists within the current working directory.

        Raises:
            typer.Exit: if the .matcha directory does not exist.
            typer.Exit: if the .matcha directory does not contain the required files to deploy resources.
        """
        if not self.tfs.check_matcha_directory_exists():
            print_error(
                f"Error, the .matcha directory does not exist in {os.getcwd()} . Please ensure you are trying to destroy resources that you have provisioned in the current working directory."
            )
            raise typer.Exit()

        if not self.tfs.check_matcha_directory_integrity():
            print_error(
                "Error, the .matcha directory does not contain files relating to deployed resources. Please ensure you are trying to destroy resources that you have provisioned in the current working directory."
            )
            raise typer.Exit()

    def _apply_terraform(self) -> None:
        """Run terraform apply to create resources on cloud.

        Raises:
            MatchaTerraformError: if 'terraform apply' failed.
        """
        with Spinner("Applying"):
            ret_code, _, err = self.tfs.apply()

            if ret_code != 0:
                raise MatchaTerraformError(tf_error=err)

        print_status(
            build_substep_success_status(
                f"{Emojis.CHECKMARK.value} Your environment has been provisioned!\n"
            )
        )

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

    def _destroy_terraform(self) -> None:
        """Destroy the provisioned resources.

        Raises:
            MatchaTerraformError: if 'terraform destroy' failed.
        """
        print()
        print_status(
            build_status(f"{Emojis.WAITING.value} Destroying your resources...")
        )
        print()
        with Spinner("Destroying"):
            ret_code, _, err = self.tfs.destroy()

            if ret_code != 0:
                raise MatchaTerraformError(tf_error=err)

    def is_approved(self, verb: str) -> bool:
        """Get approval from user to modify resources on cloud.

        Args:
            verb (str): the verb to use in the approval message.

        Returns:
            bool: True if user approves, False otherwise.
        """
        summary_message = build_resource_confirmation(
            header=f"The following resources will be {verb}ed",
            resources=[
                ("Resource group", "A resource group"),
                ("Azure Kubernetes Service (AKS)", "A kubernetes cluster"),
                (
                    "Two Storage Containers",
                    "A storage container for experiment tracking artifacts and a second for model training artifacts",
                ),
                (
                    "Seldon Core",
                    "A framework for model deployment on top of a kubernetes cluster",
                ),
                (
                    "Azure Container Registry",
                    "A container registry for storing docker images",
                ),
                ("ZenServer", "A zenml server required for remote orchestration"),
            ],
            footer=f"{verb.capitalize()}ing the resources may take approximately 20 minutes. May we suggest you grab a cup of {Emojis.MATCHA.value}?",
        )

        print_status(summary_message)
        return typer.confirm(f"Are you happy for '{verb}' to run?")

    def provision(self) -> None:
        """Provision resources required for the deployment."""
        self._check_terraform_installation()
        self._validate_terraform_config()
        self._validate_kubeconfig(base_path=".kube/config")
        self._initialize_terraform()
        self._apply_terraform()
        self._show_terraform_outputs()

    def deprovision(self) -> None:
        """Destroy the provisioned resources."""
        self._check_matcha_directory_exists()
        self._check_terraform_installation()
        self._destroy_terraform()
