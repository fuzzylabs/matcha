"""Base template that serves as a foundation for other templates to inherit from."""
import dataclasses
import glob
import json
import os
from shutil import copy, rmtree
from typing import List, Optional

from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.cli.ui.status_message_builders import (
    build_status,
    build_step_success_status,
    build_substep_success_status,
)
from matcha_ml.errors import MatchaPermissionError


@dataclasses.dataclass
class TemplateVariables:
    """Terraform template variables."""

    def __init__(self, **kwargs: str):
        """A constructor that accepts an arbitrary number of named arguments and sets them as class variables."""
        vars(self).update(kwargs)


class BaseTemplate:
    """An abstract base class that serves as the foundation for other template classes."""

    # Define additional non-tf files that are needed from the main module
    main_module_filenames: List[str] = [
        ".gitignore",
        ".terraform.lock.hcl",
    ]

    # A list of allowed file extensions.
    allowed_extensions: List[str] = ["tf", "yaml", "tpl"]

    def __init__(self, submodule_names: List[str]):
        """Initialize the class.

        Args:
            submodule_names (List[str]): A list of submodule names.
        """
        self.submodule_names = submodule_names

    def build_template_configuration(self, **kwargs: str) -> TemplateVariables:
        """Ask for variables and build the configuration.

        Args:
            **kwargs: Named arguments representing the variables.

        Returns:
            TemplateVariables: Terraform variables required by a template.
        """
        return TemplateVariables(**kwargs)

    def copy_files(
        self, files: List[str], destination: str, sub_folder_path: str = ""
    ) -> None:
        """Copy files from folders and sub folders to the destination directory.

        Args:
            files (List[str]): List of all allowed file paths in the folder/sub-folder to copy to destination.
            destination (str): destination path to write template to.
            sub_folder_path (str): Path to sub folder to create in destination. Defaults to "".
        """
        destination_folder = (
            os.path.join(destination, sub_folder_path)
            if sub_folder_path
            else destination
        )

        for source_path in files:
            filename = os.path.basename(source_path)
            destination_path = os.path.join(destination_folder, filename)
            copy(source_path, destination_path)

    def copy_main_module_files(self, template_src: str, destination: str) -> None:
        """Copy main module files from the template source to the destination.

        Args:
            template_src (str): Path of the template source directory.
            destination (str): Destination path to copy the files to.
        """
        files = [
            os.path.join(template_src, filename)
            for filename in self.main_module_filenames
        ]
        self.copy_files(files, destination)

    def copy_submodule_files(
        self, template_src: str, destination: str, verbose: Optional[bool]
    ) -> None:
        """Copy submodule files from the template source to the destination.

        Args:
            template_src (str): Path of the template source directory.
            destination (str): Destination path to copy the files to.
            verbose (Optional[bool]): Additional output is shown when True.
        """
        for submodule_name in self.submodule_names:
            submodule_destination = os.path.join(destination, submodule_name)
            os.makedirs(submodule_destination, exist_ok=True)

            for ext in self.allowed_extensions:
                file_pattern = os.path.join(template_src, submodule_name, f"*.{ext}")
                files = glob.glob(file_pattern)

                self.copy_files(files, destination, submodule_name)

            if verbose:
                print_status(
                    build_substep_success_status(
                        f"{submodule_name} module configuration was copied"
                    )
                )

    def copy_files_with_extension(
        self, template_src: str, extension: str, destination: str
    ) -> None:
        """Copy files with the specified extension from the template source to the destination.

        Args:
            template_src (str): Path of the template source directory.
            extension (str): File extension to filter files.
            destination (str): Destination path to copy the files to.
        """
        files = glob.glob(os.path.join(template_src, extension))
        self.copy_files(files, destination)

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

            self.copy_main_module_files(template_src, destination)
            self.copy_submodule_files(template_src, destination, verbose)
            self.copy_files_with_extension(template_src, "*.tf", destination)

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
