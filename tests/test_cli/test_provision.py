"""Test suite to test the provision command and all its subcommands."""
import glob
import json
import os
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from matcha_ml.cli.cli import app
from matcha_ml.templates.azure_template import DEFAULT_STACK_TF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)

RUN_TWICE = 2

REMOTE_STATE_MANAGER_PREFIX = "matcha_ml.state.remote_state_manager.RemoteStateManager"


@pytest.fixture(autouse=True)
def mock_provisioned_remote_state():
    """Mock remote state manager to have state provisioned."""
    with patch(
        "matcha_ml.core.core.RemoteStateManager.is_state_provisioned"
    ) as mock_is_state_provisioned:
        mock_is_state_provisioned.return_value = False
        yield


@pytest.fixture(autouse=True)
def mock_use_lock():
    """Mock use_lock state context manager."""
    with patch("matcha_ml.core.core.RemoteStateManager.use_lock") as mocked_use_lock:
        yield mocked_use_lock


@pytest.fixture(autouse=True)
def mock_use_remote_state():
    """Mock use_lock state context manager."""
    with patch(
        "matcha_ml.core.core.RemoteStateManager.use_remote_state"
    ) as mocked_use_remote_state:
        yield mocked_use_remote_state


def assert_infrastructure(
    destination_path: str,
    expected_tf_vars: Dict[str, str],
    check_matcha_state_file: bool = True,
):
    """Assert if the infrastructure configuration is valid.

    Args:
        destination_path (str): infrastructure config destination path
        expected_tf_vars (Dict[str, str]): expected Terraform variables
        check_matcha_state_file (bool): whether to check the matcha.state file exists and have correct value. Defaults to True.
    """
    # Test that destination path is a directory
    assert os.path.exists(destination_path)

    for module_file_name in glob.glob(os.path.join(TEMPLATE_DIR, "*.tf")):
        module_file_path = os.path.join(destination_path, module_file_name)
        assert os.path.exists(module_file_path)

    for module_name in DEFAULT_STACK_TF:
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

    if check_matcha_state_file:
        # Check that matcha state file exists and content is equal/correct
        state_file_path = os.path.join(destination_path, os.pardir, "matcha.state")
        assert os.path.exists(state_file_path)


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
    assert "Provision cloud resources." in result.stdout


def test_cli_provision_command(
    runner: CliRunner, matcha_testing_directory: str, mock_use_lock: MagicMock
):
    """Test provision command to copy the infrastructure template.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        mock_use_lock (MagicMock): mock use_lock context manager
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(
        app, ["provision"], input="uksouth\nmatcha\ndefault\ndefault\nY\n"
    )

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    state_storage_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "remote_state_storage"
    )

    resources_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "resources"
    )

    state_storage_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
    }

    resources_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
        "password": "default",
        "zenmlserver_version": "latest",
    }

    assert_infrastructure(
        state_storage_destination_path, state_storage_expected_tf_vars, False
    )
    assert_infrastructure(resources_destination_path, resources_expected_tf_vars)
    mock_use_lock.assert_called_once()


def test_cli_provision_command_with_args(
    runner: CliRunner, matcha_testing_directory: str, mock_use_lock: MagicMock
):
    """Test provision command to copy the infrastructure template with command-line arguments.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        mock_use_lock (MagicMock): mock use_lock context manager
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

    state_storage_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "remote_state_storage"
    )

    resources_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "resources"
    )

    state_storage_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
    }

    resources_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
        "password": "ninja",
        "zenmlserver_version": "latest",
    }

    assert_infrastructure(
        state_storage_destination_path, state_storage_expected_tf_vars, False
    )
    assert_infrastructure(resources_destination_path, resources_expected_tf_vars)
    mock_use_lock.assert_called_once()


def test_cli_provision_command_with_prefix(
    runner: CliRunner, matcha_testing_directory: str, mock_use_lock: MagicMock
):
    """Test provision command to copy the infrastructure template with different prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        mock_use_lock (MagicMock): mock use_lock context manager
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(
        app, ["provision"], input="uksouth\ncoffee\ndefault\ndefault\nY\n"
    )

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    state_storage_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "remote_state_storage"
    )

    resources_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "resources"
    )

    state_storage_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "coffee",
    }

    resources_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "coffee",
        "password": "default",
        "zenmlserver_version": "latest",
    }

    assert_infrastructure(
        state_storage_destination_path, state_storage_expected_tf_vars, False
    )
    assert_infrastructure(resources_destination_path, resources_expected_tf_vars)
    mock_use_lock.assert_called_once()


def test_cli_provision_command_with_default_prefix(
    runner: CliRunner, matcha_testing_directory: str, mock_use_lock: MagicMock
):
    """Test provision command to copy the infrastructure template with no prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        mock_use_lock (MagicMock): mock use_lock context manager
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(app, ["provision"], input="uksouth\n\ndefault\ndefault\nY\n")

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    state_storage_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "remote_state_storage"
    )

    resources_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "resources"
    )

    state_storage_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
    }

    resources_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
        "password": "default",
        "zenmlserver_version": "latest",
    }

    assert_infrastructure(
        state_storage_destination_path, state_storage_expected_tf_vars, False
    )
    assert_infrastructure(resources_destination_path, resources_expected_tf_vars)
    mock_use_lock.assert_called_once()


def test_cli_provision_command_with_verbose_arg(
    runner: CliRunner, matcha_testing_directory: str, mock_use_lock: MagicMock
):
    """Test that the verbose argument works and provision shows more output.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        mock_use_lock (MagicMock): mock use_lock context manager
    """
    os.chdir(matcha_testing_directory)

    result = runner.invoke(
        app, ["provision", "--verbose"], input="uksouth\n\ndefault\ndefault\nY\n"
    )

    assert result.exit_code == 0

    for verbose_output in [
        "module configuration was copied",
        "Configurations were copied",
        "Template variables were added",
        "Template configuration has finished!",
    ]:
        assert verbose_output in result.stdout

    mock_use_lock.assert_called_once()


def test_cli_provision_command_with_existing_prefix_name(
    runner: CliRunner,
    matcha_testing_directory: str,
    mock_use_lock: MagicMock,
):
    """Test whether the expected error message is prompt when user entered an existing prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        mock_use_lock (MagicMock): mock use_lock context manager
    """
    expected_error_message = "Error: You entered a resource group name prefix that has been used before, the prefix must be unique."
    os.chdir(matcha_testing_directory)

    result = runner.invoke(
        app,
        ["provision"],
        input="uksouth\nrand\nvalid\ndefault\ndefault\nN\n",
    )
    assert expected_error_message in result.stdout

    mock_use_lock.assert_not_called()


def test_cli_provision_command_with_password_mismatch(
    runner: CliRunner, matcha_testing_directory: str, mock_use_lock: MagicMock
):
    """Test provision command to copy the infrastructure template with different prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        mock_use_lock (MagicMock): mock use_lock context manager
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(
        app, ["provision"], input="uksouth\ncoffee\ndefault\nninja\nno\nno\n"
    )

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    assert "Error: The two entered values do not match." in result.stdout

    mock_use_lock.assert_not_called()
