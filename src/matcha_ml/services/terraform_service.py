"""The Terraform service interface."""
import dataclasses
import glob
import os
from pathlib import Path
from typing import Optional, Tuple

import python_terraform


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


class TerraformService:
    """TerraformService class to provision and deprovision resources."""

    # configuration required for terraform
    config: TerraformConfig = TerraformConfig()

    # terraform client
    _terraform_client: Optional[python_terraform.Terraform] = None

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

    def check_installation(self) -> bool:
        """Checks if terraform is installed on the host system.

        Raises:
            Exit: if terraform is not installed.
        """
        try:
            self.terraform_client.cmd(cmd="-help")
        except Exception:
            return False

        return True

    def verify_kubectl_config_file(self, config_path: str = ".kube/config") -> None:
        """Checks if kubeconfig is present at location ~/.kube/config.

        Args:
            config_path (str): Relative path to location of kubeconfig

        If not, it creates a empty config file.
        """
        kubeconfig_path = os.path.join(os.path.expanduser("~"), config_path)

        if not os.path.exists(kubeconfig_path):
            os.makedirs(os.path.dirname(kubeconfig_path), exist_ok=True)
            with open(kubeconfig_path, "a"):
                pass

    def check_matcha_directory_integrity(self) -> bool:
        """Checks the integrity of the .matcha directory.

        Args:
            directory_path (str): .matcha directory path

        Returns:
            bool: False if .matcha directory is empty else True.
        """
        matcha_dir_path = os.path.join(os.getcwd(), ".matcha")

        return len(glob.glob(os.path.join(matcha_dir_path, "*"))) != 0

    def check_matcha_directory_exists(self) -> bool:
        """Checks if .matcha directory exists within the current working directory.

        Returns:
            bool: True when the .matcha directory exists.
        """
        matcha_dir_path = os.path.join(os.getcwd(), ".matcha")

        return os.path.isdir(matcha_dir_path)

    def validate_config(self) -> bool:
        """Validate the configuration used for creating resources.

        Returns:
            bool: True when the config file exists.
        """
        return Path(self.config.var_file).exists()

    def get_tf_state_dir(self) -> Path:
        """Get the path of the terraform.tfstate file generated on completion of `terraform init`.

        Returns:
            Path: a Path object that represents the path to the terraform.tfstate file
        directory.
        """
        return Path(os.path.join(self.config.working_dir, "terraform.tfstate"))

    def init(self) -> Tuple[int, str, str]:
        """Run `terraform init` with the initialised Terraform client from the python_terraform module.

        Returns:
            Tuple[int, str, str]: return code of Terraform, standard output and standard error.
        """
        ret_code, out, err = self.terraform_client.init(
            capture_output=self.config.capture_output,
            raise_on_error=False,
        )

        return ret_code, out, err

    def apply(self) -> Tuple[int, str, str]:
        """Run `terraform apply` with the initialised Terraform client from the python_terraform module.

        Returns:
            Tuple[int, str, str]: return code of Terraform, standard output and standard error.
        """
        # once terraform init is success, call terraform apply
        ret_code, out, err = self.terraform_client.apply(
            input=False,
            capture_output=self.config.capture_output,
            raise_on_error=False,
            skip_plan=True,
            auto_approve=True,
        )

        return ret_code, out, err

    def destroy(self) -> Tuple[int, str, str]:
        """Destroy the provisioned resources with the initialised Terraform client from the python_terraform module..

        Returns:
            Tuple[int, str, str]: return code of terraform, standard output and standard error.
        """
        # Reference: https://github.com/beelit94/python-terraform/issues/108
        ret_code, out, err = self.terraform_client.destroy(
            capture_output=self.config.capture_output,
            raise_on_error=False,
            force=python_terraform.IsNotFlagged,
            auto_approve=True,
        )

        return ret_code, out, err
