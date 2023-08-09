"""Run terraform templates to provision and deprovision resources."""
import os
import shutil

from matcha_ml.runners.base_runner import BaseRunner
from matcha_ml.state.matcha_state import MatchaStateService


class AzureRunner(BaseRunner):
    """A Runner class provides methods that interface with the Terraform service to facilitate the provisioning and deprovisioning of resources."""

    def __init__(self) -> None:
        """Initialize AzureRunner class."""
        super().__init__()

    def remove_matcha_dir(self) -> None:
        """Removes the project's .matcha directory"."""
        project_directory = os.getcwd()
        target = os.path.join(project_directory, ".matcha")
        if os.path.exists(target):
            shutil.rmtree(target)

    def provision(self) -> MatchaStateService:
        """Provision resources required for the deployment.

        Returns:
            (MatchaStateService): a MatchaStateService instance initialized with Terraform output
        """
        self._check_terraform_installation()
        self._validate_terraform_config()
        self._validate_kubeconfig(base_path=".kube/config")
        self._initialize_terraform(msg="Matcha")
        self._apply_terraform(msg="Matcha")
        tf_output = self.tfs.terraform_client.output()
        return MatchaStateService(terraform_output=tf_output)

    def deprovision(self) -> None:
        """Destroy the provisioned resources."""
        self._check_matcha_directory_exists()
        self._check_terraform_installation()
        self._initialize_terraform(msg="Matcha", destroy=True)
        self._destroy_terraform(msg="Matcha")
