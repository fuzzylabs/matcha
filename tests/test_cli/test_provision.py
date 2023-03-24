"""Test suite to test the provision command and all its subcommands."""
import glob
import json
import os
from typing import Dict

import pytest

from matcha_ml.cli.cli import app
from src.matcha_ml.cli.provision import (
    SUBMODULE_NAMES,
    TemplateVariables,
    build_template,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, os.pardir, os.pardir, "src", "infrastructure")


def assert_infrastructure(destination_path: str, expected_tf_vars: Dict[str, str]):
    """Assert if the infrastructure configuration is valid

    Args:
        destination_path (str): infrastructure config destination path
        expected_tf_vars (Dict[str, str]): expected Terraform variables
    """
    # Test that destination path is a directory
    assert os.path.exists(destination_path)

    for module_file_name in glob.glob(os.path.join(TEMPLATE_DIR, "*.tf")):
        module_file_path = os.path.join(destination_path, module_file_name)
        assert os.path.exists(module_file_path)

    for module_name in SUBMODULE_NAMES:
        for module_file_name in glob.glob(
            os.path.join(TEMPLATE_DIR, module_name, "*.tf")
        ):
            module_file_path = os.path.join(
                destination_path, module_name, module_file_name
            )
            assert os.path.exists(module_file_path)

    # Check that Terraform variables file exists and content is equal/correct
    variables_file_path = os.path.join(destination_path, "terraform.tfvars.json")
    assert os.path.exists(variables_file_path)

    with open(variables_file_path, "r") as f:
        tf_vars = json.load(f)

    assert tf_vars == expected_tf_vars


@pytest.fixture
def template_src_path() -> str:
    """Fixture for the test infrastructure template path.

    Returns:
        str: template path
    """
    template_dir = os.path.join(BASE_DIR, os.pardir, os.pardir, "src", "infrastructure")

    return template_dir


def test_cli_provision_command_help(runner):
    """Test cli for provision command help.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke provision command
    result = runner.invoke(app, ["provision", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Provision cloud resources with a template." in result.stdout


def test_cli_provision_command(runner, matcha_testing_directory):
    """Test provision command to copy the infrastructure template.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(app, ["provision"], input="\nuksouth\nno\n")

    # Exit code 1 exists because we add a prompt "no" to provision resources
    assert result.exit_code == 1

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_args(runner, matcha_testing_directory):
    """Test provision command to copy the infrastructure template with command-line arguments.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(
        app, ["provision", "--location", "uksouth", "--prefix", "matcha"], input="no\n"
    )

    # Exit code 1 exists because we add a prompt "no" to provision resources
    assert result.exit_code == 1

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_prefix(runner, matcha_testing_directory):
    """Test provision command to copy the infrastructure template with different prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(app, ["provision"], input="coffee\nukwest\nno\n")

    # Exit code 1 exists because we add a prompt "no" to provision resources
    assert result.exit_code == 1

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "ukwest", "prefix": "coffee"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_build_template(matcha_testing_directory, template_src_path):
    """Test that the template is built and copied to correct locations.

    Args:
        matcha_testing_directory (str): Temporary .matcha directory path
        template_src_path (str): Existing template directory path
    """
    config = TemplateVariables("uksouth")

    destination_path = os.path.join(matcha_testing_directory, "infrastructure")

    build_template(config, template_src_path, destination_path)

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)
