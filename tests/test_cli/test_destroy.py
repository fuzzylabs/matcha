"""Test suite to test the destroy command and all its subcommands."""
import os
from unittest.mock import patch

import pytest

from matcha_ml.cli.cli import app


@pytest.fixture(autouse=True)
def mock_provisioned_remote_state():
    """Mock remote state manager to have state provisioned."""
    with patch("matcha_ml.cli.destroy.RemoteStateManager") as mock_state_manager_class:
        mock_state_manager = mock_state_manager_class.return_value
        mock_state_manager.is_state_provisioned.return_value = True
        yield


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
    runner, matcha_testing_directory
):
    """Test provision command when there no existing resources deployed.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
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
