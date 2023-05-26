"""Run terraform templates to provision and deprovision resources."""
import os
from typing import Optional, Tuple

import typer

from matcha_ml.cli.ui.emojis import Emojis
from matcha_ml.cli.ui.print_messages import print_error, print_status
from matcha_ml.cli.ui.spinner import Spinner
from matcha_ml.cli.ui.status_message_builders import (
    build_resource_confirmation,
    build_status,
    build_substep_success_status,
)
from matcha_ml.errors import MatchaTerraformError
from matcha_ml.services.terraform_service import TerraformConfig, TerraformService

SPINNER = "dots"


class BaseRunner:
    """A BaseRunner class provides methods that interface with the Terraform service to facilitate the provisioning and deprovisioning of resources."""

    def __init__(self, working_dir: Optional[str] = None) -> None:
        """Initialize BaseRunner class.

        Args:
            working_dir (Optional[str]): Working directory for terraform. Defaults to None.
        """
        if working_dir is not None:
            working_dir = working_dir
        else:
            working_dir = TerraformConfig().working_dir
        self.terraform_config = TerraformConfig(working_dir=working_dir)
        self.tfs = TerraformService(self.terraform_config)
        self.tf_state_dir = self.tfs.get_tf_state_dir()
        self.state_file = self.tfs.config.state_file

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

    def _initialize_terraform(self, msg: str = "") -> None:
        """Run terraform init to initialize Terraform .

        Raises:
            MatchaTerraformError: if 'terraform init' failed.
            msg (str) : Message to display. Default is empty string.
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
                    f"{Emojis.CHECKMARK.value} {msg} {Emojis.MATCHA.value} initialized!\n"
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

    def _destroy_terraform(self, msg: str = "") -> None:
        """Destroy the provisioned resources.

        Raises:
            MatchaTerraformError: if 'terraform destroy' failed.
            msg (str) : Message to display. Default is empty string.
        """
        print()
        print_status(
            build_status(f"{Emojis.WAITING.value} Destroying {msg} resources...")
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

    def provision(self) -> Optional[Tuple[str, str, str]]:
        """Provision resources required for the deployment."""
        raise NotImplementedError

    def deprovision(self) -> None:
        """Destroy the provisioned resources."""
        raise NotImplementedError