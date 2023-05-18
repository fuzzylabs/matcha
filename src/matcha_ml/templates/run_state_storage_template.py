"""Run terraform templates to provision and deprovision state bucket resource."""
import os
from typing import Tuple

import typer

from matcha_ml.cli.ui.emojis import Emojis
from matcha_ml.cli.ui.print_messages import (
    print_error,
    print_status,
)
from matcha_ml.cli.ui.spinner import Spinner
from matcha_ml.cli.ui.status_message_builders import (
    build_status,
    build_substep_success_status,
)
from matcha_ml.errors import MatchaTerraformError
from matcha_ml.services.terraform_service import TerraformConfig, TerraformService


class TemplateRunner:
    """A Runner class provides methods that interface with the Terraform service to facilitate the provisioning and deprovisioning of the state bucket."""

    terraform_config = TerraformConfig(
        working_dir=os.path.join(
            os.getcwd(), ".matcha", "infrastructure/remote_state_storage"
        )
    )
    tfs: TerraformService = TerraformService(terraform_config)

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

    def _initialize_terraform(self) -> None:
        """Run terraform init to initialize Terraform .

        Raises:
            MatchaTerraformError: if 'terraform init' failed.
        """
        with Spinner("Initializing"):
            ret_code, _, err = self.tfs.init()

            if ret_code != 0:
                print_error("The command 'terraform init' failed.")
                raise MatchaTerraformError(tf_error=err)

        print_status(
            build_substep_success_status("Remote state management initialized!\n")
        )

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

    def _get_terraform_output(self) -> Tuple[str, str]:
        """Return the account name and the container name from terraform output.

        Returns:
            Tuple[str, str]: account name and the container name.
        """
        tf_outputs = self.tfs.terraform_client.output()

        account_name = ""
        container_name = ""

        for output_name, properties in tf_outputs.items():
            property_name = output_name.replace("remote_state_storage_", "")
            if property_name == "account_name":
                account_name = properties["value"]
            else:
                container_name = properties["value"]

        return account_name, container_name

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

    def provision(self) -> Tuple[str, str]:
        """Provision the azure storage bucket for remote state management."""
        self._check_terraform_installation()
        self._validate_terraform_config()
        self._initialize_terraform()
        self._apply_terraform()

        return self._get_terraform_output()

    def deprovision(self) -> None:
        """Destroy the provisioned resources."""
        self._check_matcha_directory_exists()
        self._check_terraform_installation()
        self._destroy_terraform()
