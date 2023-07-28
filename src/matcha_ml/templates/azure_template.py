"""Build a template for provisioning resources on Azure using terraform files."""
from typing import Optional

from matcha_ml.state import MatchaState, MatchaStateService
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
    "data_version_control_storage",
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
        config_dict = vars(config)
        _ = config_dict.pop("password", None)
        config_dict["resource-group-name"] = f"{config_dict['prefix']}-resources"
        initial_state_file_dict = {"cloud": config_dict}
        matcha_state = MatchaState.from_dict(initial_state_file_dict)
        MatchaStateService(matcha_state=matcha_state)
