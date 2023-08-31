"""Build a template for provisioning resources on Azure using terraform files."""
import json
import os
import shutil
from shutil import rmtree
from typing import List, Optional

from matcha_ml.cli.ui.print_messages import print_error, print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_status,
    build_step_success_status,
    build_substep_success_status,
)
from matcha_ml.config.matcha_config import MatchaConfigService
from matcha_ml.errors import MatchaPermissionError
from matcha_ml.state import MatchaState, MatchaStateService
from matcha_ml.templates.base_template import BaseTemplate, TemplateVariables

DEFAULT_STACK = [
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
LLM_STACK = DEFAULT_STACK + [
    "chroma",
    "chroma/chroma_helm",
    "chroma/chroma_helm/templates",
]


class AzureTemplate(BaseTemplate):
    """A template tailored for provisioning the resources on azure.

    Inherits:
        BaseTemplate: The base template class.
    """

    def __init__(self, submodule_names: List[str]) -> None:
        """Initialize the StateStorageTemplate with the submodule names.

        Args:
            submodule_names (List[str]): A list of submodule names.
        """
        super().__init__(submodule_names)

    @staticmethod
    def empty_directory_except_files(directory: str, except_files: List[str]) -> None:
        """Empties a directory of all files and folders except for a list of file names.

        Args:
            directory (str): Directory name to clean.
            except_files (List[str]): List of file names to be excluded from removal.
        """
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path) and item not in except_files:
                    os.remove(item_path)
                elif os.path.isdir(item_path) and item not in except_files:
                    shutil.rmtree(item_path)
        except (OSError, FileNotFoundError) as e:
            print_error(f"Error while emptying directory '{directory}': {e}")

    @staticmethod
    def concatenate_files(source_file: str, target_file: str) -> None:
        """Takes the contents of one file and concatenates it to a target file.

        Args:
            source_file (str): File to copy contents from.
            target_file (str): Destination to add source file contents to.
        """
        try:
            with open(source_file) as source, open(target_file, "a") as target:
                target.write(source.read())
        except (OSError, FileNotFoundError) as e:
            print_error(f"Error while concatenating files: {e}")

    @staticmethod
    def recursively_copy_files(source_dir: str, target_dir: str) -> None:
        """Copy all files within a source location to a target location.

        Args:
            source_dir (str): The source directory containing files to copy.
            target_dir (str): The target directory to copy files to.
        """
        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            for item in os.listdir(source_dir):
                source_item = os.path.join(source_dir, item)
                target_item = os.path.join(target_dir, item)

                if os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item)
                elif os.path.exists(target_item):
                    # Concatenate the source file content to the target file
                    AzureTemplate.concatenate_files(source_item, target_item)
                else:
                    shutil.copy2(source_item, target_item)
        except (OSError, FileNotFoundError) as e:
            print_error(f"Error while copying files: {e}")

    def build_template(
        self,
        config: TemplateVariables,
        template_src: str,
        destination: str,
        verbose: Optional[bool] = False,
    ) -> None:
        """Build and copy the template to the project directory.

        Args:
            config (TemplateVariables): variables to apply to the template.
            template_src (str): path of the template to use.
            destination (str): destination path to write template to.
            verbose (bool, optional): additional output is shown when True. Defaults to False.

        Raises:
            MatchaPermissionError: when there are no write permissions on the configuration destination
        """
        try:
            print_status(build_status("\nBuilding configuration template..."))

            # Override configuration if it already exists
            if os.path.exists(destination):
                rmtree(destination)

            os.makedirs(destination, exist_ok=True)

            if verbose:
                print_status(
                    build_substep_success_status(
                        f"Ensure template destination directory: {destination}"
                    )
                )

            stack = {"common"}
            stack_component = MatchaConfigService.read_matcha_config().find_component(
                "stack"
            )
            if stack_component is not None:
                for item in stack_component.properties:
                    if item.name != "name":
                        stack.add(item.value)

            self.empty_directory_except_files(
                destination, [".terraform", ".terraform.lock.hcl", "terraform.tfstate"]
            )
            for module in stack:
                source_directory = os.path.join(template_src, f"{module}")
                self.recursively_copy_files(source_directory, destination)

                if verbose:
                    print_status(
                        build_substep_success_status(
                            f"{module} module configuration was copied"
                        )
                    )

            if verbose:
                print_status(
                    build_substep_success_status("Configurations were copied.")
                )

            configuration_destination = os.path.join(
                destination, "terraform.tfvars.json"
            )
            with open(configuration_destination, "w") as f:
                json.dump(vars(config), f)

            if verbose:
                print_status(
                    build_substep_success_status("Template variables were added.")
                )

        except PermissionError:
            raise MatchaPermissionError(
                f"Error - You do not have permission to write the configuration. Check if you have write permissions for '{destination}'."
            )

        if verbose:
            print_status(
                build_substep_success_status("Template configuration has finished!")
            )

        print_status(
            build_step_success_status(
                f"The configuration template was written to {destination}"
            )
        )

        print()

        # Add matcha.state file one directory above the template
        config_dict = vars(config)
        _ = config_dict.pop("password", None)
        config_dict["resource-group-name"] = f"{config_dict['prefix']}-resources"
        initial_state_file_dict = {"cloud": config_dict}
        matcha_state = MatchaState.from_dict(initial_state_file_dict)
        MatchaStateService(matcha_state=matcha_state)
