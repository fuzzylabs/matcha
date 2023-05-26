"""Test suite to test the destroy command and all its subcommands."""
import json
import os
from typing import Iterable
from unittest.mock import MagicMock, patch

import pytest

from matcha_ml.cli.cli import app
from matcha_ml.templates.azure_template.run_azure_template import AzureTemplateRunner


@pytest.fixture(autouse=True)
def mock_provisioned_remote_state() -> Iterable[MagicMock]:
    """Mock remote state manager to have state provisioned.

    Returns:
        MagicMock: mock of an RemoteStateManager instance
    """
    with patch("matcha_ml.cli.destroy.RemoteStateManager") as mock_state_manager_class:
        mock_state_manager = mock_state_manager_class.return_value
        mock_state_manager.is_state_provisioned.return_value = True
        yield mock_state_manager


def test_cli_destroy_command_help(runner):
    """Test cli for provision command help.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke destroy command
    result = runner.invoke(app, ["destroy", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Destroy the provisioned cloud resources." in result.stdout


def test_cli_destroy_command_with_no_provisioned_resources(
    runner, matcha_testing_directory, mock_provisioned_remote_state: MagicMock
):
    """Test provision command when there no existing resources deployed.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
        mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
    """
    os.chdir(matcha_testing_directory)

    # Invoke destroy command
    with patch(
        "matcha_ml.templates.azure_template.azure_template.check_current_deployment_exists"
    ) as check_deployment_exists:
        check_deployment_exists.return_value = False
        result = runner.invoke(app, ["destroy"])

    assert (
        "Error - you cannot destroy resources that have not been provisioned yet."
        in result.stdout
    )
    
    mock_provisioned_remote_state.use_lock.assert_called_once()


def test_cli_destroy_command_updates_matcha_state(runner, matcha_testing_directory):
    """Test provision command updates the matcha state file when resources (excluding resource group and state bucket) are destroyed.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
    """
    os.chdir(matcha_testing_directory)

    matcha_infrastructure_dir = os.path.join(".matcha", "infrastructure", "resources")
    matcha_state_file_path = os.path.join(".matcha", "infrastructure", "matcha.state")

    os.makedirs(matcha_infrastructure_dir)

    state_file_resources = {
        "cloud": {
            "prefix": "test",
            "location": "ukwest",
            "flavor": "azure",
            "resource-group-name": "test_resources",
        },
        "id": {"matcha_uuid": "TestStateID"},
        "container-registry": {
            "flavor": "azure",
            "registry-name": "azure_registry_name",
            "registry-url": "azure_container_registry",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
    }

    with open(matcha_state_file_path, "w") as f:
        json.dump(state_file_resources, f)

    expected_matcha_state_contents = {
        "cloud": {
            "prefix": "test",
            "location": "ukwest",
            "flavor": "azure",
            "resource-group-name": "test_resources",
        },
        "id": {"matcha_uuid": "TestStateID"},
    }

    # Invoke destroy command
    with patch(
        "matcha_ml.cli.destroy.check_current_deployment_exists"
    ) as check_deployment_exists, patch.object(
        AzureTemplateRunner, "state_file", matcha_state_file_path
    ):
        check_deployment_exists.return_value = True
        runner.invoke(
            app,
            ["destroy"],
            input="Y\n",
        )

    with open(matcha_state_file_path) as f:
        matcha_state_data = json.load(f)

    assert matcha_state_data == expected_matcha_state_contents
