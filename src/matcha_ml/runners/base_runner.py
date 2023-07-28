"""Run terraform templates to provision and deprovision resources."""
import os
from multiprocessing.pool import ThreadPool
from typing import Optional, Tuple

import typer

from matcha_ml.cli.ui.emojis import Emojis
from matcha_ml.cli.ui.print_messages import print_error, print_status
from matcha_ml.cli.ui.spinner import Spinner
from matcha_ml.cli.ui.status_message_builders import (
    build_status,
    build_substep_success_status,
    terraform_status_update,
)
from matcha_ml.errors import MatchaTerraformError
from matcha_ml.services.terraform_service import (
    TerraformConfig,
    TerraformService,
)

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

    def _initialize_terraform(self, msg: str = "", destroy: bool = False) -> None:
        """Run terraform init to initialize Terraform .

        Raises:
            MatchaTerraformError: if 'terraform init' failed.
            msg (str) : Message to display. Default is empty string.
            destroy (bool): whether this function is being called in a destructive context
        """
        if self.tf_state_dir.exists():
            if not destroy:
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
                tf_result = self.tfs.init()

                if tf_result.return_code != 0:
                    print_error("The command 'terraform init' failed.")
                    raise MatchaTerraformError(tf_error=tf_result.std_err)

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

    def _apply_terraform(self, msg: str = "") -> None:
        """Run terraform apply to create resources on cloud.

        Args:
            msg (str) : Name of the type of resource (e.g. "Remote State" or "Matcha").

        Raises:
            MatchaTerraformError: if 'terraform apply' failed.
        """
        with Spinner("Applying") as spinner:
            pool = ThreadPool(processes=1)
            _ = pool.apply_async(terraform_status_update, (spinner,))

            tf_result = self.tfs.apply()

            pool.terminate()

            if tf_result.return_code != 0:
                raise MatchaTerraformError(tf_error=tf_result.std_err)

        if msg:
            print_status(
                build_substep_success_status(
                    f"{Emojis.CHECKMARK.value} {msg} resources have been provisioned!\n"
                )
            )
        else:
            print_status(
                build_substep_success_status(
                    f"{Emojis.CHECKMARK.value} Resources have been provisioned!\n"
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
            tf_result = self.tfs.destroy()

            if tf_result.return_code != 0:
                raise MatchaTerraformError(tf_error=tf_result.std_err)

    def provision(self) -> Optional[Tuple[str, str, str]]:
        """Provision resources required for the deployment."""
        raise NotImplementedError

    def deprovision(self) -> None:
        """Destroy the provisioned resources."""
        raise NotImplementedError
