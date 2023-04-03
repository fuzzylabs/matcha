"""Run terraform templates to provision and deprovision resources."""
import dataclasses
import json
import os
from pathlib import Path
from typing import Optional

import python_terraform
import typer
from rich import print, print_json
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from matcha_ml.errors import MatchaTerraformError

MLFLOW_TRACKING_URL = "mlflow-tracking-url"
ZENML_STORAGE_PATH = "zenml-storage-path"
ZENML_CONNECTION_STRING = "zenml-connection-string"
K8S_CONTEXT = "k8s-context"


SPINNER = "dots"


@dataclasses.dataclass
class TerraformConfig:
    """Configuration required for terraform."""

    # Path to terraform template are stored
    working_dir: str = os.path.join(os.getcwd(), ".matcha", "infrastructure")

    # state file to store output after terraform apply
    state_file: str = os.path.join(working_dir, "matcha.state")

    # variables file
    var_file: str = os.path.join(working_dir, "terraform.tfvars.json")

    # if set to False terraform output will be printed to stdout/stderr
    # else no output will be printed and (ret_code, out, err) tuple will be returned
    capture_output: bool = True


@dataclasses.dataclass
class Emojis:
    """Emojis class for displaying emojis."""

    checkmark_emoji: str = "✔"

    cross_emoji: str = "❌"

    waiting_emoji: str = "⏳"

    matcha_emoji: str = "🍵"


class TerraformService:
    """TerraformService class to provision and deprovision resources."""

    # configuration required for terraform
    config: TerraformConfig = TerraformConfig()

    # terraform client
    _terraform_client: Optional[python_terraform.Terraform] = None

    # emoji instance to display emojis
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
        except Exception:
            return False

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

    def validate_config(self) -> None:
        """Validate the configuration used for creating resources.

        Raises:
            Exit: If `terraform.tfvars.json` file not found in current directory.
        """
        var_file = Path(self.config.var_file)

        if not var_file.exists():
            print(
                "The file terraform.tfvars.json was not found in the "
                f"current directory at {self.config.var_file}. Please "
                "verify if it exists."
            )
            raise typer.Exit()

    def is_approved(self, verb: str) -> bool:
        """Get approval from user to modify resources on cloud.

        Args:
            verb: The verb to use in the approval message.

        Returns:
            bool: True if user approves, False otherwise.
        """
        summary_message = f"""The following resources will be {verb}ed:
1. [yellow] Resource group [/yellow]: A resource group
2. [yellow] Azure Kubernetes Service (AKS) [/yellow]: A kubernetes cluster
3. [yellow] Azure Storage Container [/yellow]: A storage container

{verb.capitalize()}ing the resources may take up to 10 minutes. May we suggest you to grab a cup of 🍵?
"""

        print()
        print(summary_message)
        return typer.confirm(f"Are you happy for '{verb}' to run?")

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
                "matcha {self.emojis.matcha_emoji} has already been initialised. Skipping this step..."
            )

        else:
            print()
            print(
                f"{self.emojis.waiting_emoji} Brewing matcha {self.emojis.matcha_emoji}..."
            )
            print()

            # run terraform init
            with Progress(
                SpinnerColumn(spinner_name=SPINNER),
                TimeElapsedColumn(),
            ) as progress:
                progress.add_task(description="Initializing", total=None)

                ret_code, _, err = self.terraform_client.init(
                    capture_output=self.config.capture_output,
                    raise_on_error=False,
                )
                if ret_code != 0:
                    raise MatchaTerraformError(tf_error=err)

                print(
                    f"[green] {self.emojis.checkmark_emoji} Matcha {self.emojis.matcha_emoji} initialised! [/green]"
                )
                print()

                # Create a directory to avoid running init multiple times
                previous_temp_dir.mkdir(parents=True, exist_ok=True)

        print()
        print(f"{self.emojis.waiting_emoji} Provisioning your resources...")
        print()

        # once terraform init is success, call terraform apply
        with Progress(
            SpinnerColumn(spinner_name=SPINNER),
            TimeElapsedColumn(),
        ) as progress:
            progress.add_task(description="Applying", total=None)

            ret_code, _, err = self.terraform_client.apply(
                input=False,
                capture_output=self.config.capture_output,
                raise_on_error=False,
                skip_plan=True,
                auto_approve=True,
            )
            if ret_code != 0:
                raise MatchaTerraformError(tf_error=err)

        print()
        print(
            f"[green] {self.emojis.checkmark_emoji} Your environment has been provisioned! [/green]"
        )

    def provision(self) -> None:
        """Provision resources required for the deployment.

        Raises:
            Exit: if approval is not given by user.
        """
        self.check_installation()

        self.validate_config()

        if self.is_approved(verb="provision"):
            self._init_and_apply()
            self.show_terraform_outputs()

        else:
            print(
                "You decided to cancel - if you change your mind, then run 'matcha provision' again."
            )
            raise typer.Exit()

    def _destroy(self) -> None:
        """Destroy the provisioned resources."""
        print()
        print(f"{self.emojis.waiting_emoji} Destroying your resources...")
        print()

        with Progress(
            SpinnerColumn(spinner_name=SPINNER),
            TimeElapsedColumn(),
        ) as progress:
            progress.add_task(description="Destroying", total=None)

            # Reference: https://github.com/beelit94/python-terraform/issues/108
            ret_code, _, err = self.terraform_client.destroy(
                capture_output=self.config.capture_output,
                raise_on_error=False,
                force=python_terraform.IsNotFlagged,
                auto_approve=True,
            )
            if ret_code != 0:
                raise MatchaTerraformError(tf_error=err)

    def deprovision(self) -> None:
        """Deprovision the resources.

        Raises:
            Exit: if approval is not given by user.
        """
        self.check_installation()

        if self.is_approved(verb="destroy"):
            self._destroy()

        else:
            print(
                "You decided to cancel - your resources will remain active! If you change your mind, then run 'matcha destory' again."
            )
            raise typer.Exit()

    def write_outputs_state(self) -> None:
        """Write the outputs of the terraform deployment to the state json file."""
        outputs = {
            MLFLOW_TRACKING_URL: self.terraform_client.output(
                MLFLOW_TRACKING_URL, full_value=True
            ),
            ZENML_STORAGE_PATH: self.terraform_client.output(
                ZENML_STORAGE_PATH, full_value=True
            ),
            ZENML_CONNECTION_STRING: self.terraform_client.output(
                ZENML_CONNECTION_STRING, full_value=True
            ),
            K8S_CONTEXT: self.terraform_client.output(K8S_CONTEXT, full_value=True),
        }

        # dump specific terraform output to state file
        with open(self.config.state_file, "w") as fp:
            json.dump(outputs, fp, indent=4)

    def show_terraform_outputs(self) -> None:
        """Print the terraform outputs from state file."""
        # copy terraform output to state file
        self.write_outputs_state()

        print()
        print("Here are the endpoints for what's been provisioned")
        # print terraform output from state file
        with open(self.config.state_file) as fp:
            print_json(fp.read())
        print()
