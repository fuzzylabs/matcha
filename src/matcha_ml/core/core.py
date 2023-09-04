"""The core functionality for Matcha API."""
import os
from enum import Enum, EnumMeta
from typing import Optional

from matcha_ml.cli._validation import get_command_validation
from matcha_ml.cli.ui.print_messages import (
    print_json,
    print_status,
)
from matcha_ml.cli.ui.resource_message_builders import (
    dict_to_json,
    hide_sensitive_in_output,
)
from matcha_ml.cli.ui.status_message_builders import build_status, build_warning_status
from matcha_ml.config import (
    MatchaConfigComponent,
    MatchaConfigComponentProperty,
    MatchaConfigService,
)
from matcha_ml.constants import DEFAULT_STACK, LLM_STACK, STACK_MODULES
from matcha_ml.core._validation import is_valid_prefix, is_valid_region
from matcha_ml.errors import MatchaError, MatchaInputError
from matcha_ml.runners import AzureRunner
from matcha_ml.services.analytics_service import AnalyticsEvent, track
from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.state import MatchaStateService, RemoteStateManager
from matcha_ml.state.matcha_state import MatchaState
from matcha_ml.templates.azure_template import (
    DEFAULT_STACK_TF,
    LLM_STACK_TF,
    AzureTemplate,
)


class StackTypeMeta(
    EnumMeta
):  # this is probably overkill, but we might need it if we'll support custom stacks later.
    """Metaclass for the StackType Enum."""

    def __contains__(self, item: str) -> bool:  # type: ignore
        """Dunder method for checking if an item is a member of the enum.

        Args:
            item (str): the quantity to check for in the Enum.

        Returns:
            True if item is a member of the Enum, False otherwise.
        """
        try:
            self(item)
        except ValueError:
            return False
        else:
            return True


class StackType(Enum, metaclass=StackTypeMeta):
    """Enum defining matcha stack types."""

    DEFAULT = "default"
    LLM = "llm"


def infer_zenml_version() -> str:
    """Check the zenml version of the local environment against the version matcha is expecting."""
    try:
        import zenml  # type: ignore

        version = str(zenml.__version__)
        print(
            f"\nMatcha detected zenml version {version}, so will use the same version on the remote resources."
        )
    except ImportError:
        version = "latest"
        print(
            "\nMatcha didn't find a zenml installation locally, so will install the latest release of zenml on the "
            "remote resources."
        )

    return version


def _show_terraform_outputs(matcha_state: MatchaState) -> None:
    """Print the formatted Terraform outputs.

    Args:
        matcha_state (MatchaState): Terraform outputs in a MatchaState format.
    """
    print_status(build_status("Here are the endpoints for what's been provisioned"))
    resources_dict = hide_sensitive_in_output(matcha_state.to_dict())
    resources_json = dict_to_json(resources_dict)
    print_json(resources_json)


@track(event_name=AnalyticsEvent.GET)
def get(
    resource_name: Optional[str],
    property_name: Optional[str],
) -> MatchaState:
    """Return information regarding a previously provisioned resource based on the resource and property names provided.

    The information is returned in the form of a `MatchaState` object containing various `MatchaStateComponent` objects.
    The `MatchaStateComponent` objects in turn hold `MatchaResource` and `MatchaResourceProperty` components.
    If no resource name is provided, all resources are returned.

    Examples:
        >>> get("cloud", "resource-group-name")
        MatchaState(components=[MatchaStateComponent(resource=MatchaResource(name='cloud'),
        properties=[MatchaResourceProperty(name='resource-group-name', value='test_resources')])])

        >>> get("experiment-tracker", "flavor")
        MatchaState(components=[MatchaStateComponent(resource=MatchaResource(name='experiment-tracker'),
        properties=[MatchaResourceProperty(name='flavor', value='mlflow')])])

    Args:
        resource_name (Optional[str]): name of the resource to get information for.
        property_name (Optional[str]): the property of the resource to get.

    Returns:
        MatchaState: the information of the provisioned resource.

    Raises:
        MatchaError: Raised when the matcha state has not been initialized
        MatchaError: Raised when the matcha.state file does not exist
        MatchaInputError: Raised when the resource or property name does not exist in the matcha.state file
    """
    if resource_name:
        resource_name = resource_name.lower()

    if property_name:
        property_name = property_name.lower()

    remote_state = RemoteStateManager()

    if not remote_state.is_state_provisioned():
        raise MatchaError(
            "Error - matcha state has not been initialized, nothing to get."
        )

    if not MatchaStateService.state_exists():
        # if the state file doesn't exist, then download it from the remote
        remote_state.download(os.getcwd())

    matcha_state_service = MatchaStateService()

    with remote_state.use_lock():
        local_hash = matcha_state_service.get_hash_local_state()
        remote_hash = remote_state.get_hash_remote_state(
            matcha_state_service.matcha_state_path
        )

        if local_hash != remote_hash:
            remote_state.download(os.getcwd())

            matcha_state_service = MatchaStateService()

        if resource_name:
            get_command_validation(
                resource_name,
                matcha_state_service.get_resource_names(),
                "resource type",
            )

        if resource_name and property_name:
            get_command_validation(
                property_name,
                matcha_state_service.get_property_names(resource_name),
                "property",
            )

        result = matcha_state_service.fetch_resources_from_state_file(
            resource_name, property_name
        )

    return result


@track(event_name=AnalyticsEvent.DESTROY)
def destroy() -> None:
    """Destroy the provisioned cloud resources.

    Decommission the cloud infrastructure built by Matcha when provision has been called either historically or during
    this session. After calling destroy, the resources provisioned by matcha should no longer be active on your
    chosen provider's UI.

    Raises:
        Matcha Error: where no state has been provisioned.
    """
    remote_state_manager = RemoteStateManager()

    if not remote_state_manager.is_state_provisioned():
        raise MatchaError(
            "Error - resources that have not been provisioned cannot be destroyed. Run 'matcha provision' to get started!"
        )

    template_runner = AzureRunner()
    with remote_state_manager.use_lock(
        destroy=True
    ), remote_state_manager.use_remote_state(destroy=True):
        template_runner.deprovision()
        remote_state_manager.deprovision_remote_state()


def analytics_opt_out() -> None:
    """Disable the collection of anonymous usage data.

    More information regarding why we collect usage data, and how it is used, can be found
    [here](https://mymatcha.ai/privacy/).
    """
    GlobalParameters().analytics_opt_out = True


def analytics_opt_in() -> None:
    """Enable the collection of anonymous usage data (enabled by default).

    More information regarding why we collect usage data, and how it is used, can be found
    [here](https://mymatcha.ai/privacy/).
    """
    GlobalParameters().analytics_opt_out = False


def remove_state_lock() -> None:
    """Unlock the remote state.

    Note:
        The remote state is synced to a state file kept locally. The state will be locked when in use, and removing the
        state lock and making changes could result in a state file not consistent with what Matcha expects.
    """
    remote_state = RemoteStateManager()
    remote_state.unlock()


@track(event_name=AnalyticsEvent.PROVISION)
def provision(
    location: str,
    prefix: str,
    password: str,
    verbose: Optional[bool] = False,
) -> MatchaState:
    """Provision cloud resources using existing Matcha Terraform templates.

    Provision cloud resources in the location provided. Provide a prefix for the Azure group's name and a password for
    the provisioned server. To show more output than the default, set verbose to True.

    Examples:
        >>> provision(location="ukwest", prefix="myexample", password="example_password", verbose=False)
        MatchaState(components=[MatchaStateComponent(resource=MatchaResource(name='cloud'),
            properties=[MatchaResourceProperty(name='location', value='ukwest'),
            MatchaResourceProperty(name='prefix', value='test')])])


    Args:
        location (str): Azure location in which all resources will be provisioned.
        prefix (str): Prefix used for all resources.
        password (str): Password for the deployment server.
        verbose (bool optional): additional output is show when True. Defaults to False.

    Returns:
        MatchaState: the information of the provisioned resources.

    Raises:
        MatchaError: If resources are already provisioned.
        MatchaError: If prefix is not valid.
        MatchaError: If region is not valid.
    """
    remote_state_manager = RemoteStateManager()
    template_runner = AzureRunner()

    if MatchaStateService.state_exists():
        matcha_state_service = MatchaStateService()
        if matcha_state_service.is_local_state_stale():
            template_runner.remove_matcha_dir()

    if remote_state_manager.is_state_stale():
        if verbose:
            print_status(
                build_warning_status(
                    "Matcha has detected a stale state file. This means that your local configuration is out of sync with the remote state, the resource group may have been removed. Deleting existing state config."
                )
            )
        MatchaConfigService.delete_matcha_config()
        template_runner.remove_matcha_dir()

    if remote_state_manager.is_state_provisioned():
        raise MatchaError(
            "Error - Matcha has detected that there are resources already provisioned. Use 'matcha destroy' to remove the existing resources before trying to provision again."
        )

    # Input variable checks
    try:
        prefix = prefix.lower()
        _ = is_valid_prefix(prefix)
        _ = is_valid_region(location)
    except MatchaInputError as e:
        raise e

    if MatchaConfigService.get_stack() is None:
        stack_set("default")

    # Provision resource group and remote state storage
    remote_state_manager.provision_remote_state(location, prefix)

    with remote_state_manager.use_lock(), remote_state_manager.use_remote_state():
        project_directory = os.getcwd()
        destination = os.path.join(
            project_directory, ".matcha", "infrastructure", "resources"
        )

        stack = MatchaConfigService.get_stack()
        if stack is not None:
            stack_property = stack.find_property("name")
            if stack_property is not None:
                stack_name = stack_property.value

        template = os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "infrastructure",
            "modules",
        )

        azure_template = AzureTemplate(
            LLM_STACK_TF if stack_name == StackType.LLM.value else DEFAULT_STACK_TF
        )

        zenml_version = infer_zenml_version()
        config = azure_template.build_template_configuration(
            location=location,
            prefix=prefix,
            password=password,
            zenmlserver_version=zenml_version,
        )
        azure_template.build_template(config, template, destination, verbose)

        matcha_state_service = template_runner.provision()

        if verbose:
            _show_terraform_outputs(matcha_state_service._state)

        return matcha_state_service.fetch_resources_from_state_file()


def stack_set(stack_name: str) -> None:
    """A function for updating the stack type in the local matcha.config.json file.

    Note: This cannot be run once there are provisioned resources.

    Examples:
        >>> stack_set(stack_name='default')

    Args:
        stack_name (str): the name of the type of stack to be specified in the config file.

    Raises:
        MatchaInputError: if the stack_name is not a valid stack type
        MatchaError: if there are already resources provisioned.
    """

    def _create_stack_component(stack_type: StackType) -> MatchaConfigComponent:
        """Create the set of configuration component for the stack.

        Args:
            stack_type (StackType): the type of stack to create.

        Returns:
            MatchaConfigComponent: the stack component.
        """
        stack = MatchaConfigComponent(
            name="stack",
            properties=[
                MatchaConfigComponentProperty(name="name", value=stack_type.value)
            ],
        )

        stack.properties += LLM_STACK if stack_type == StackType.LLM else DEFAULT_STACK

        return stack

    if RemoteStateManager().is_state_provisioned():
        raise MatchaError(
            "The remote resources are already provisioned. Changing the stack now will not "
            "change the remote state."
        )

    if stack_name.lower() not in StackType:
        raise MatchaInputError(f"{stack_name} is not a valid stack type.")

    stack = _create_stack_component(stack_type=StackType(stack_name.lower()))

    MatchaConfigService.update(stack)


def stack_add(module_type: str, module_flavor: str) -> None:
    """A function for adding a module by name to the stack.

    Examples:
        >>> stack_add(module_type='experiment_tracker', module_flavor='mlflow')

    Args:
        module_type (str): The type of the module to add e.g. 'experiment_tracker'.
        module_flavor (str): The flavor of module to add e.g. 'mlflow'.

    Raises:
        MatchaInputError: if the stack_name is not a valid stack type
        MatchaError: if there are already resources provisioned.
    """
    module_type = module_type.lower()
    module_flavor = module_flavor.lower()

    if RemoteStateManager().is_state_provisioned():
        raise MatchaError(
            "The remote resources are already provisioned. Changing the stack now will not "
            "change the remote state."
        )

    if STACK_MODULES.get(module_type) is None:
        raise MatchaInputError(f"The module type '{module_type}' does not exist.")

    module_properties = STACK_MODULES.get(module_type, {}).get(module_flavor)

    if module_properties is None:
        raise MatchaInputError(
            f"The module type '{module_type}' does not have a flavor '{module_flavor}'."
        )

    MatchaConfigService.add_property("stack", module_properties)

    # Update stack name to custom
    MatchaConfigService.add_property(
        "stack", MatchaConfigComponentProperty("name", "custom")
    )


def stack_remove(module_type: str) -> None:
    """A function for removing a module by name in the stack.

    Examples:
        >>> stack_remove(module_type='experiment_tracker')

    Args:
        module_type (str): The name of the module to remove.

    Raises:
        MatchaError: if there are already resources provisioned.
        MatchaInputError: if the module_type is not a valid module within the current stack.
    """
    if RemoteStateManager().is_state_provisioned():
        raise MatchaError(
            "The remote resources are already provisioned. Changing the stack now will not "
            "change the remote state."
        )

    module_type = module_type.lower()

    matcha_config = MatchaConfigService.read_matcha_config()
    matcha_stack_component = matcha_config.find_component("stack")

    if matcha_stack_component:
        if matcha_stack_component.find_property(module_type):
            MatchaConfigService.remove_property("stack", module_type)
            MatchaConfigService.add_property(
                "stack", MatchaConfigComponentProperty("name", "custom")
            )
        else:
            raise MatchaInputError(
                f"Module '{module_type}' does not exist in the current stack."
            )
    else:
        raise MatchaError(
            "No Matcha 'stack' component found in the local 'matcha.config.json' file. Please run 'matcha stack set' or matcha stack add'."
        )
