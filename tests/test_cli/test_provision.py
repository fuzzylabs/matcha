"""Test suite to test the provision command and all its subcommands."""
import json
import os
import shutil
import tempfile

import pytest

from matcha_ml.cli.cli import app
from src.matcha_ml.cli.provision import TemplateVariables, build_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def matcha_testing_folder():
    """A fixture for creating and removing the .matcha folder for storing and moving files.

    Yields:
        dir: a folder for temporarily storing and moving files from tests.
    """
    temp_dir = tempfile.TemporaryDirectory()

    # tests are executed at this point
    yield temp_dir.name

    # delete temp folder
    temp_dir.cleanup()


@pytest.fixture
def template_src_path():
    """_summary_"""
    template_dir = os.path.join(BASE_DIR, os.pardir, os.pardir, "src", "infrastructure")

    return template_dir


def test_cli_provision_command_help(runner):
    """Test cli for provision command help."""
    # Invoke provision command
    result = runner.invoke(app, ["provision", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Provision cloud resources with a template." in result.stdout


def test_build_template(matcha_testing_folder, template_src_path):
    """_summary_

    Args:
        matcha_testing_folder (str): Temporary .matcha directory path
        template_src_path (str): Existing template directory path
    """
    config = TemplateVariables("uksouth")

    destination_path = os.path.join(matcha_testing_folder, "infrastructure")

    build_template(config, template_src_path, destination_path)

    module_file_names = ["main.tf", "variables.tf", "output.tf"]

    module_names = ["aks", "resource_group"]

    # Test that destination path is a directory
    print(destination_path)
    assert os.path.exists(destination_path)

    for module_file_name in module_file_names:
        module_file_path = os.path.join(destination_path, module_file_name)
        assert os.path.exists(module_file_path)

        for module_name in module_names:
            module_file_path = os.path.join(
                destination_path, module_name, module_file_name
            )
            assert os.path.exists(module_file_path)

    # Check that Terraform variables file exists and content is equal/correct
    variables_file_path = os.path.join(destination_path, "terraform.tfvars.json")
    assert os.path.exists(variables_file_path)

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    with open(variables_file_path, "r") as f:
        tf_vars = json.load(f)

    assert tf_vars == expected_tf_vars
