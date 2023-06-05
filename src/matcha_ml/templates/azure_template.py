"""Build a template for provisioning resources on Azure using terraform files."""
import json
import os
from typing import Optional

from matcha_ml.cli._validation import check_current_deployment_exists
from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.state import MatchaStateService
from matcha_ml.templates.base_template import BaseTemplate, TemplateVariables

SUBMODULE_NAMES = [
    "aks",
    "resource_group",
    "mlflow_module",
    "storage",
    "seldon",
    "zenml_storage",
    "zen_server",
    "azure_container_registry",
    "zen_server/zenml_helm",
    "zen_server/zenml_helm/templates",
]


class AzureTemplate(BaseTemplate):
    """A template tailored for provisioning the resources on azure.

    Inherits:
        BaseTemplate: The base template class.
    """

    def __init__(self) -> None:
        """Initialize the StateStorageTemplate with the submodule names.

        Args:
            submodule_names (List[str]): A list of submodule names.
        """
        super().__init__(SUBMODULE_NAMES)

    def check_current_configuration_is_provisioned(self, path: str) -> bool:
        """Check if a deployed configuration already exists.

        Args:
            path (str): path to the infrastructure configuration

        Returns:
            bool: True, if the current configuration is provisioned
        """
        if os.path.exists(path) and check_current_deployment_exists():
            matcha_state_service = MatchaStateService()
            resource_group_name = matcha_state_service.fetch_resources_from_state_file(
                "cloud", "prefix"
            )["cloud"]["prefix"]
            warning_msg = f"\nWARNING: Matcha has detected that a deployment already exists in Azure with the resource group name '{resource_group_name}'."
            print_status(warning_msg)
            return True
        return False

    def build_template(
        self,
        config: TemplateVariables,
        template_src: str,
        destination: str,
        verbose: Optional[bool] = False,
    ) -> None:
        """Builds a template using the provided configuration and copies it to the destination.

        Args:
            config (TemplateVariables): variables to apply to the template.
            template_src (str): path of the template to use.
            destination (str): destination path to write template to.
            verbose (Optional[bool]): additional output is shown when True. Defaults to False.
        """
        super().build_template(config, template_src, destination, verbose)

        # Add matcha.state file one directory above the template
        state_file_destination = os.path.join(destination, os.pardir, "matcha.state")

        config_dict = vars(config)
        _ = config_dict.pop("password", None)
        initial_state_file_dict = {"cloud": config_dict}

        with open(state_file_destination, "w") as f:
            json.dump(initial_state_file_dict, f)
