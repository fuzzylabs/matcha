"""Build a template for provisioning remote state storage on Azure using terraform files."""
from matcha_ml.templates.base_template import BaseTemplate

SUBMODULE_NAMES = ["resource_group", "state_storage"]


class RemoteStateTemplate(BaseTemplate):
    """A template tailored for provisioning the state storage on azure.

    Inherits:
        BaseTemplate: The base template class.
    """

    def __init__(self) -> None:
        """Initialize the StateStorageTemplate with the submodule names.

        Args:
            submodule_names (List[str]): A list of submodule names.
        """
        super().__init__(SUBMODULE_NAMES)
