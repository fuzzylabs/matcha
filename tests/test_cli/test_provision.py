"""Test suite to test the provision command and all its subcommands."""
import glob
import json
import os
from typing import Dict
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from matcha_ml.cli._validation import LONGEST_RESOURCE_NAME, MAXIMUM_RESOURCE_NAME_LEN
from matcha_ml.cli.cli import app
from matcha_ml.templates.build_templates.azure_template import SUBMODULE_NAMES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)


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

    # Check that matcha state file exists and content is equal/correct
    state_file_path = os.path.join(destination_path, "matcha.state")
    assert os.path.exists(state_file_path)

    with open(state_file_path) as f:
        tf_vars = json.load(f)

    _ = expected_tf_vars.pop("password", None)
    expected_matcha_state_vars = {"cloud": expected_tf_vars}
    assert tf_vars == expected_matcha_state_vars


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
    result = runner.invoke(
        app, ["provision"], input="uksouth\nmatcha\ndefault\ndefault\nY\n"
    )
    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
        "password": "default",
    }

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
        app,
        [
            "provision",
            "--location",
            "uksouth",
            "--prefix",
            "matcha",
            "--password",
            "ninja",
        ],
        input="Y\n",
    )

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha", "password": "ninja"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_prefix(runner, matcha_testing_directory):
    """Test provision command to copy the infrastructure template with different prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(
        app, ["provision"], input="uksouth\ncoffee\ndefault\ndefault\nY\n"
    )

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {
        "location": "uksouth",
        "prefix": "coffee",
        "password": "default",
    }

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_default_prefix(runner, matcha_testing_directory):
    """Test provision command to copy the infrastructure template with no prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(app, ["provision"], input="uksouth\n\ndefault\ndefault\nY\n")

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
        "password": "default",
    }

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

    result = runner.invoke(
        app, ["provision", "--verbose"], input="uksouth\n\ndefault\ndefault\nY\n"
    )

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
            "uksouth\n-matcha-\nvalid\ndefault\ndefault\nno\n",
            "Error: Resource group name prefix can only contain alphanumeric characters.",
        ),
        (
            "uksouth\n12\nvalid\ndefault\ndefault\nno\n",
            "Error: Resource group name prefix cannot contain only numbers.",
        ),
        (
            "uksouth\ngood$prefix#\nvalid\ndefault\ndefault\nno\n",
            "Error: Resource group name prefix can only contain alphanumeric characters.",
        ),
        (
            "uksouth\nareallyloingprefix\nvalid\ndefault\ndefault\nno\n",
            f"Resource group name prefix must be between 3 and {MAXIMUM_RESOURCE_NAME_LEN - len(LONGEST_RESOURCE_NAME)} characters long.",
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
        input="uksouth\nrand\nvalid\ndefault\ndefault\nN\n",
    )
    assert expected_error_message in result.stdout


def test_cli_provision_command_override(
    runner, matcha_testing_directory, mocked_azure_client
):
    """Test provision command to override the configuration file within the .matcha directory.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
        mocked_azure_client (AzureClient) : Mocked Azure client
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command for the first time which creates the .matcha directory
    runner.invoke(
        app,
        [
            "provision",
            "--location",
            "uksouth",
            "--prefix",
            "matcha",
            "--password",
            "ninja",
        ],
        input="Y\n",
    )

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    # Touch a 'dummy.tf' file in the infrastructure configuration directory within the .matcha directory
    with open(os.path.join(destination_path, "dummy.tf"), "a"):
        ...

    mocked_azure_client.resource_group_state.return_value = None
    # Invoke provision command for a second time, which overwrites the existing .matcha directory and removes the 'dummy.tf' file
    runner.invoke(
        app,
        [
            "provision",
            "--location",
            "uksouth",
            "--prefix",
            "matcha",
            "--password",
            "ninja",
        ],
        input="Y\nY\n",
    )

    # Checks the 'dummy.tf' file is not present within the overwritten .matcha directory
    assert not os.path.exists(os.path.join(destination_path, "dummy.tf"))

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha", "password": "ninja"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_password_mismatch(runner, matcha_testing_directory):
    """Test provision command to copy the infrastructure template with different prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(
        app, ["provision"], input="uksouth\ncoffee\ndefault\nninja\nno\nno\n"
    )

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    assert "Error: The two entered values do not match." in result.stdout


def test_cli_provision_command_reuse(runner, matcha_testing_directory):
    """Test provision command to reuse the configuration file within the .matcha directory.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command for the first time which creates the .matcha directory
    runner.invoke(
        app,
        ["provision", "--location", "uksouth", "--prefix", "matcha"],
        input="default\ndefault\nY\n",
    )

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    # Touch a 'dummy.tf' file in the infrastructure configuration directory within the .matcha directory
    with open(os.path.join(destination_path, "dummy.tf"), "a"):
        ...

    # Invoke provision command for a second time, electing to reuse the existing .matcha directory and therefore retain the 'dummy.tf' file
    runner.invoke(
        app,
        ["provision", "--location", "uksouth", "--prefix", "matcha"],
        input="default\ndefault\nn\nY\n",
    )

    # Checks the 'dummy.tf' file is present within the reused .matcha directory
    assert os.path.exists(os.path.join(destination_path, "dummy.tf"))

    expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
        "password": "default",
    }

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_provisioned_resources(
    runner, matcha_testing_directory
):
    """Test provision command when there are already existing resources deployed.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command for the first time which creates the .matcha directory
    runner.invoke(
        app,
        [
            "provision",
            "--location",
            "uksouth",
            "--prefix",
            "matcha",
            "--password",
            "ninja",
        ],
        input="Y\n",
    )

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    # Touch a 'dummy.tf' file in the infrastructure configuration directory within the .matcha directory
    with open(os.path.join(destination_path, "dummy.tf"), "a"):
        ...

    # Mock functions such that a deployment on Azure exists
    with patch(
        "matcha_ml.templates.build_templates.azure_template.check_current_deployment_exists"
    ) as check_deployment_exists, patch(
        "matcha_ml.templates.build_templates.azure_template.MatchaStateService.fetch_resources_from_state_file"
    ) as fetch_resources_from_state_file:
        check_deployment_exists.return_value = True
        fetch_resources_from_state_file.return_value = {
            "cloud": {"resource-group-name": "matcha-resources"}
        }
        # Invoke provision command for a second time, which overwrites the existing .matcha directory and removes the 'dummy.tf' file
        result = runner.invoke(
            app,
            [
                "provision",
                "--location",
                "uksouth",
                "--prefix",
                "matcha",
                "--password",
                "ninja",
            ],
            input="Y\nY\n",
        )

    # Checks the 'dummy.tf' file is not present within the overwritten .matcha directory
    assert not os.path.exists(os.path.join(destination_path, "dummy.tf"))

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha", "password": "ninja"}

    assert_infrastructure(destination_path, expected_tf_vars)

    assert (
        "WARNING: Matcha has detected that a deployment already exists in Azure"
        in result.stdout
    )
