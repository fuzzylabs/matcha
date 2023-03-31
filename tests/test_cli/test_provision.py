"""Test suite to test the provision command and all its subcommands."""
import glob
import json
import os
from typing import Dict
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from matcha_ml.cli.cli import app
from matcha_ml.templates.build_templates.azure_template import SUBMODULE_NAMES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)


@pytest.fixture(scope="session", autouse=True)
def check_azure_is_authenticated_mock():
    """Mock the return result of check_azure_is_authenticated.

    Yields:
        str: the mock authentication result.
    """
    with patch("matcha_ml.cli.region_validation.check_azure_is_authenticated") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture(scope="session", autouse=True)
def get_azure_subscription_client_mock():
    """Mock the return result of get_azure_subscription_client.

    Yields:
        str: the mock Azure subscription client.
    """
    with patch("matcha_ml.cli.region_validation.get_azure_subscription_client") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture(scope="session", autouse=True)
def get_azure_locations_mock():
    """Mock the return result of get_azure_locations.

    Yields:
        str: the mock Azure regions/locations.
    """
    with patch("matcha_ml.cli.region_validation.get_azure_locations") as mock:
        mock.return_value = ["uksouth", "ukwest"]
        yield mock


@pytest.fixture(scope="session", autouse=True)
def resource_group_name_mock():
    """Mock the return result of get_existing_resource_group_names.

    Yields:
        str: the mock existing resource group name.
    """
    with patch(
        "matcha_ml.cli.prefix_validation.get_existing_resource_group_names"
    ) as mock:
        mock.return_value = "repeated-prefix-resources"
        yield mock


def assert_infrastructure(destination_path: str, expected_tf_vars: Dict[str, str]):
    """Assert if the infrastructure configuration is valid.

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

    with open(variables_file_path) as f:
        tf_vars = json.load(f)

    assert tf_vars == expected_tf_vars


def test_cli_provision_command_help(runner: CliRunner):
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


def test_cli_provision_command(
    runner,
    matcha_testing_directory,
):
    """Test provision command to copy the infrastructure template.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(app, ["provision"], input="\nuksouth\nmatcha\nno\n")

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_args(
    runner,
    matcha_testing_directory,
):
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

    # Exit code 0 means there was no error
    assert result.exit_code == 0

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
    result = runner.invoke(app, ["provision"], input="ukwest\ncoffee\nno\nno\n")

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "ukwest", "prefix": "coffee"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_default_prefix(runner, matcha_testing_directory):
    """Test provision command to copy the infrastructure template with no prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(app, ["provision"], input="ukwest\n\nno\nno\n")

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "ukwest", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_verbose_arg(
    runner,
    matcha_testing_directory,
):
    """Test that the verbose argument works and provision shows more output.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    result = runner.invoke(app, ["provision", "--verbose"], input="uksouth\n\nno\n")

    assert result.exit_code == 0

    for verbose_output in [
        "module configuration was copied",
        "Configuration was copied",
        "Template variables were added",
        "Template configuration has finished!",
    ]:
        assert verbose_output in result.stdout


@pytest.mark.parametrize(
    "user_input, expected_output",
    [
        (
            "uksouth\n-1-\nvalid-prefix\nno\n",
            "Error: Resource group name prefix cannot start or end with a hyphen.",
        ),
        (
            "uksouth\n12\nvalid-prefix\nno\n",
            "Error: Resource group name prefix must be between 3 and 24 characters long.",
        ),
        (
            "uksouth\ngood$prefix#\nvalid-prefix\nno\n",
            "Error: Resource group name prefix must contain only alphanumeric characters and hyphens.",
        ),
    ],
)
def test_cli_provision_command_prefix_rule(
    runner: CliRunner,
    matcha_testing_directory: str,
    user_input: str,
    expected_output: str,
):
    """Test whether the prefix validation function prompt an error message when user entered an invalid prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        user_input (str): prefix entered by user
        expected_output (str): the expected error message
    """
    os.chdir(matcha_testing_directory)

    result = runner.invoke(app, ["provision"], input=user_input)

    assert expected_output in result.stdout


def test_cli_provision_command_with_existing_prefix_name(
    runner: CliRunner,
    matcha_testing_directory: str,
):
    """Test whether the expected error message is prompt when user entered an existing prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    expected_error_message = "Error: You entered a resource group name prefix that have been used before, prefix must be unique."
    os.chdir(matcha_testing_directory)

    result = runner.invoke(
        app,
        ["provision"],
        input="uksouth\nrepeated-prefix\nvalid-prefix\nno\n",
    )

    assert expected_error_message in result.stdout


def test_cli_provision_command_override(runner, matcha_testing_directory):
    """Test provision command to override the configuration.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    runner.invoke(
        app, ["provision", "--location", "uksouth", "--prefix", "matcha"], input="no\n"
    )

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    # Touch a file in the infrastructure configuration directory
    with open(os.path.join(destination_path, "dummy.tf"), "a"):
        ...

    runner.invoke(
        app,
        ["provision", "--location", "uksouth", "--prefix", "matcha"],
        input="y\nno\n",
    )

    assert not os.path.exists(os.path.join(destination_path, "dummy.tf"))

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_reuse(runner, matcha_testing_directory):
    """Test provision command to reuse the configuration.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    runner.invoke(
        app, ["provision", "--location", "uksouth", "--prefix", "matcha"], input="no\n"
    )

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    # Touch a file in the infrastructure configuration directory
    with open(os.path.join(destination_path, "dummy.tf"), "a"):
        ...

    runner.invoke(
        app,
        ["provision", "--location", "uksouth", "--prefix", "matcha"],
        input="n\nno\n",
    )

    assert os.path.exists(os.path.join(destination_path, "dummy.tf"))

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)
