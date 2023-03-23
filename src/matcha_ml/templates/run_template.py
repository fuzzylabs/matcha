"""Run terraform templates to provision and deprovision resources."""
import dataclasses
import json
import os
from pathlib import Path
from typing import Optional

import python_terraform
import typer
from python_terraform import TerraformCommandError
from rich import print
from rich.console import Console

err_console = Console(stderr=True)
MLFLOW_TRACKING_URL = "mlflow-tracking-url"


@dataclasses.dataclass
class TerrformConfig:
    """Configuration required for terraform."""

    # Path to terraform template are stored
    working_dir: str = os.path.join(os.getcwd(), ".matcha", "infrastructure")

    # state file to store output after terraform apply
    state_file: str = os.path.join(working_dir, "matcha.state")

    # variables file
    var_file: str = os.path.join(working_dir, "terraform.tfvars.json")


@dataclasses.dataclass
class Emojis:
    """Emojis class."""

    checkmark_emoji: str = "✔"

    cross_emoji: str = "❌"

    waiting_emoji: str = "⏳"

    neutral_emoji: str = "🤔"


class TerraformService:
    """TerraformService class to provision and deprovision resources."""

    # configuration required for terraform
    config: TerrformConfig = TerrformConfig()

    _terraform_client: Optional[python_terraform.Terraform] = None

    emojis: Emojis = Emojis()

    @property
    def terraform_client(self) -> python_terraform.Terraform:
        """Initialize and/or return the terraform client.

        Returns:
            python_terraform.Terraform: The terraform client.
        """
        if self._terraform_client is None:
            self._terraform_client = python_terraform.Terraform(
                working_dir=self.config.working_dir, var_file=self.config.var_file
            )
        return self._terraform_client

    def _is_terraform_installed(self) -> bool:
        """Check if terraform is installed on host machine.

        Returns:
            bool: True if terraform is installed, False otherwise.
        """
        try:
            self.terraform_client.cmd(cmd="-help")
        except TerraformCommandError:
            return False

        print(
            f"[green] {self.emojis.checkmark_emoji} Terraform is installed on host system. [/green]"
        )
        return True

    def check_installation(self) -> None:
        """Checks if terraform is installed on the host system.

        Raises:
            Exit: if terraform is not installed.
        """
        if not self._is_terraform_installed():
            print(f"[red] {self.emojis.cross_emoji} Terraform is not installed. [/red]")
            print(
                "Terraform is required for to run and was not found installed on your machine."
                "Please visit https://learn.hashicorp.com/tutorials/terraform/install-cli to install it."
            )
            raise typer.Exit()

    def _init_and_apply(self) -> None:
        """Run terraform init and apply to create resources on cloud.

        Raises:
            Exit: if terraform is not installed.
        """
        # this directory gets created after a successful init command
        previous_temp_dir = Path(
            os.path.join(self.terraform_client.working_dir, ".temp")
        )

        if previous_temp_dir.exists():
            print(
                f"{self.emojis.neutral_emoji} Terraform already initialized. Skipping terraform init..."
            )
        else:

            print(f"{self.emojis.waiting_emoji} Running terraform init command...")
            ret_code, _, _ = self.terraform_client.init(capture_output=False)

            if ret_code != 0:
                err_console.print_exception("The command 'terraform init' failed.")
                raise typer.Exit()

            print(
                f"[green] {self.emojis.checkmark_emoji} Terraform init success. [/green]"
            )

            # Create a directory to avoid running init multiple times
            previous_temp_dir.mkdir(parents=True, exist_ok=True)

        print(f"{self.emojis.waiting_emoji} Running terraform apply command...")

        # once terraform init is success, call terraform apply
        self.terraform_client.apply(
            # var=vars,
            input=False,
            capture_output=False,
            raise_on_error=True,
        )

        print(
            f"[green] {self.emojis.checkmark_emoji} Terraform deployment complete. [/green]"
        )

    def validate_config(self) -> None:
        """Validate the configuration used for creating resources.

        Raises:
            Exit: If `terraform.tfvars.json` file not found in current directory.
        """
        var_file = Path(self.config.var_file)

        if not var_file.exists():
            err_console.print_exception(
                "The file terraform.tfvars.json was not found in the "
                f"current directory at {self.config.var_file}. Please "
                "verify if it exists."
            )
            raise typer.Exit()

    def provision(self) -> None:
        """Provision resources required for the deployment."""
        self.check_installation()
        self.validate_config()
        self._init_and_apply()
        self.write_outputs_state()

    def _destroy(self) -> None:
        """Destroy the provisioned resources."""
        print(f"{self.emojis.waiting_emoji} Running terraform destroy command...")

        self.terraform_client.destroy(
            capture_output=False, raise_on_error=True, force=python_terraform.IsFlagged
        )

    def deprovision(self, force: bool = False) -> None:
        """Deprovision the resources.

        Args:
            force: if True, all resources will be forced destroyed.
        """
        self.check_installation()
        self._destroy()

    def write_outputs_state(self) -> None:
        """Write the outputs of the terraform deployment to the outputs.json file."""
        outputs = {
            MLFLOW_TRACKING_URL: self.terraform_client.output(
                MLFLOW_TRACKING_URL, full_value=True
            )
        }

        # dump specific terraform output to state file
        with open(self.config.state_file, "w") as fp:
            json.dump(outputs, fp, indent=4)
