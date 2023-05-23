"""Test suite for base template."""
import glob
import json
import os
from typing import Dict, Tuple

import pytest

from matcha_ml.templates.build_templates.base_template import (
    BaseTemplate,
    TemplateVariables,
)

SUBMODULE_NAMES = ["test_submodule_1", "test_submodule_2"]


@pytest.fixture
def base_template() -> BaseTemplate:
    """A base template object for testing.

    Returns:
        BaseTemplate: the base template.
    """
    return BaseTemplate(SUBMODULE_NAMES)


def assert_infrastructure(
    template_dir: str, destination_path: str, expected_tf_vars: Dict[str, str]
):
    """Asserts the validity of the infrastructure configuration.

    Args:
        template_dir (str): Path to the directory containing the infrastructure template files.
        destination_path (str): Path to the destination directory of the infrastructure configuration.
        expected_tf_vars (Dict[str, str]): Expected Terraform variables.
    """
    # Test that destination path is a directory
    assert os.path.exists(destination_path)

    for module_file_name in glob.glob(os.path.join(template_dir, "*.tf")):
        module_file_path = os.path.join(destination_path, module_file_name)
        assert os.path.exists(module_file_path)

    for module_name in SUBMODULE_NAMES:
        for module_file_name in glob.glob(
            os.path.join(template_dir, module_name, "*.tf")
        ):
            module_file_path = os.path.join(
                destination_path, module_name, module_file_name
            )
            assert os.path.exists(module_file_path)

    # Check that Terraform variables file exists and content is equal/correct
    variables_file_path = os.path.join(destination_path, "terraform.tfvars.json")
    assert os.path.exists(variables_file_path)

    with open(variables_file_path) as f:
        tf_vars = json.load(f)

    assert tf_vars == expected_tf_vars


def test_build_template_configuration(base_template: BaseTemplate):
    """Verify if the build template configuration function correctly generates the expected TemplateVariables object with the intended variables.

    Args:
        base_template (BaseTemplate): The BaseTemplate object being tested.
    """
    template_variables = base_template.build_template_configuration(
        location="test-location", prefix="test-prefix"
    )

    expected_variables = {"location": "test-location", "prefix": "test-prefix"}

    assert vars(template_variables) == expected_variables

    assert isinstance(template_variables, TemplateVariables)


def test_copy_files(
    tmp_path: str, matcha_testing_directory: str, base_template: BaseTemplate
):
    """Test the copy_files function to verify the file copying functionality of a BaseTemplate object.

    Args:
        tmp_path (str): The temporary directory path provided by pytest.
        matcha_testing_directory (str): The path to the matcha testing directory.
        base_template (BaseTemplate): The BaseTemplate object being tested.
    """
    # Create a test file in the temporary directory
    test_file_path = os.path.join(tmp_path, "test_file_1.tf")
    with open(test_file_path, "a"):
        ...

    # Copy the test file to the matcha testing directory
    base_template.copy_files([str(test_file_path)], matcha_testing_directory)

    # Verify that the copied file exists in the matcha testing directory
    expected_file_path = os.path.join(matcha_testing_directory, "test_file_1.tf")
    assert os.path.exists(expected_file_path)

    # Test copy_files when a sub folder path is passed
    matcha_testing_directory_sub_directory = os.path.join(
        matcha_testing_directory, "test_sub_folder"
    )
    os.makedirs(matcha_testing_directory_sub_directory)

    # Copy the test file to the matcha testing sub directory
    base_template.copy_files(
        [str(test_file_path)], matcha_testing_directory_sub_directory
    )

    # Verify that the copied file exists in the matcha testing sub directory
    expected_file_path = os.path.join(
        matcha_testing_directory_sub_directory, "test_file_1.tf"
    )
    assert os.path.exists(expected_file_path)


def test_copy_main_module_files(
    mock_infrastructure_directory: Tuple[str, str, str, str],
    matcha_testing_directory: str,
    base_template: BaseTemplate,
):
    """Test the copy_main_module_files function to verify the copying of main module files using a BaseTemplate object.

    Args:
        mock_infrastructure_directory (Tuple[str, str, str, str]): A tuple containing the paths to the infrastructure directory, main module directory, and submodule directories.
        matcha_testing_directory (str): The path to the matcha testing directory.
        base_template (BaseTemplate): The BaseTemplate object being tested.
    """
    # Unpack the mock_infrastructure_directory tuple
    _, template_src, _, _ = mock_infrastructure_directory

    # Copy the main module files to the matcha testing directory using the BaseTemplate object
    base_template.copy_main_module_files(template_src, matcha_testing_directory)

    expected_files = base_template.main_module_filenames

    # Check if each expected file exists in the matcha testing directory
    for file in expected_files:
        assert os.path.exists(os.path.join(matcha_testing_directory, file))


def test_copy_submodule_files(
    mock_infrastructure_directory: Tuple[str, str, str, str],
    matcha_testing_directory: str,
    base_template: BaseTemplate,
):
    """Test the copy_submodule_files function to verify the copying of submodule files using a BaseTemplate object.

    Args:
        mock_infrastructure_directory (Tuple[str, str, str, str]): A tuple containing the paths to the infrastructure directory, main module directory, and submodule directories.
        matcha_testing_directory (str): The path to the matcha testing directory.
        base_template (BaseTemplate): The BaseTemplate object being tested.
    """
    _, template_src, _, _ = mock_infrastructure_directory
    base_template.copy_submodule_files(template_src, matcha_testing_directory, True)

    for module_name in SUBMODULE_NAMES:
        for module_file_name in glob.glob(
            os.path.join(template_src, module_name, "*.tf")
        ):
            module_file_path = os.path.join(
                matcha_testing_directory, module_name, module_file_name
            )
            assert os.path.exists(module_file_path)


def test_copy_files_with_extension(
    mock_infrastructure_directory: Tuple[str, str, str, str],
    matcha_testing_directory: str,
    base_template: BaseTemplate,
):
    """Test copy_files_with_extension function to verify the copying of files with a specific extension using a BaseTemplate object.

    Args:
        mock_infrastructure_directory (Tuple[str, str, str, str]): A tuple containing the paths to the infrastructure directory, main module directory, and submodule directories.
        matcha_testing_directory (str): The path to the matcha testing directory.
        base_template (BaseTemplate): The BaseTemplate object being tested.
    """
    allowed_extension = "*.yaml"

    # Using submodule_2_dir as there are two different file extension types
    _, _, _, submodule_2_dir = mock_infrastructure_directory
    base_template.copy_files_with_extension(
        submodule_2_dir, allowed_extension, matcha_testing_directory
    )

    expected_file = os.path.join(matcha_testing_directory, "test_file_2.yaml")
    unexpected_file = os.path.join(matcha_testing_directory, "test_file_3.tpl")

    assert os.path.exists(expected_file)
    assert not os.path.exists(unexpected_file)


def test_build_template(
    matcha_testing_directory: str,
    mock_infrastructure_directory: Tuple[str, str, str, str],
    base_template: BaseTemplate,
):
    """Test that the template is built and copied to correct locations.

    Args:
        matcha_testing_directory (str): Temporary .matcha directory path
        mock_infrastructure_directory (Tuple[str, str, str, str]): mock infrastructure directory structure
        base_template (BaseTemplate): base template object
    """
    _, template_src_path, _, _ = mock_infrastructure_directory
    config = TemplateVariables(location="test-location", prefix="test-prefix")

    destination_path = os.path.join(
        matcha_testing_directory, "infrastructure", "test_resource"
    )

    base_template.build_template(config, template_src_path, destination_path)

    expected_tf_vars = {"location": "test-location", "prefix": "test-prefix"}

    assert_infrastructure(template_src_path, destination_path, expected_tf_vars)
