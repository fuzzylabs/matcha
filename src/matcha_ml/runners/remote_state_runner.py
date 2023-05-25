"""Run terraform templates to provision and deprovision state bucket resource."""
import os
from typing import Tuple

from matcha_ml.runners.base_runner import BaseRunner


class RemoteStateRunner(BaseRunner):
    """A RemoteStateRunner class that provisioning and deprovisioning resources for the remote state."""

    def __init__(
        self,
        working_dir=os.path.join(
            os.getcwd(), ".matcha", "infrastructure", "remote_state_storage"
        ),
    ) -> None:
        super().__init__(working_dir=working_dir)

    def _get_terraform_output(self) -> Tuple[str, str, str]:
        """Return the account name and the container name from terraform output.

        Returns:
            Tuple[str, str]: account name, the container name and azure resource_group_name.
        """
        tf_outputs = self.tfs.terraform_client.output()

        account_name = ""
        container_name = ""
        resource_group_name = ""

        prefix = "remote_state_storage"
        account_name = tf_outputs[f"{prefix}_account_name"]["value"]
        resource_group_name = tf_outputs[f"{prefix}_resource_group_name"]["value"]
        container_name = tf_outputs[f"{prefix}_container_name"]["value"]

        return account_name, container_name, resource_group_name

    def provision(self) -> Tuple[str, str, str]:
        """Provision resources required for the deployment.

        Returns:
            Tuple[str, str]: account name, the container name and azure resource_group_name.
        """
        self._check_terraform_installation()
        self._validate_terraform_config()
        self._validate_kubeconfig(base_path=".kube/config")
        self._initialize_terraform(msg="Remote State")
        self._apply_terraform()
        return self._get_terraform_output()

    def deprovision(self) -> None:
        """Destroy the provisioned resources."""
        self._check_matcha_directory_exists()
        self._check_terraform_installation()
        self._destroy_terraform(msg="Remote State")
