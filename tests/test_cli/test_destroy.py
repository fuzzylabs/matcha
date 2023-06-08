"""Test suite to test the destroy command and all its subcommands."""
import os
from typing import Iterable
from unittest.mock import MagicMock, patch

import pytest

from matcha_ml.cli.cli import app


@pytest.fixture(autouse=True)
def mock_remote_state_manager() -> Iterable[MagicMock]:
    """Mock remote state manager to have state provisioned.

    Yields:
        MagicMock: mock of an RemoteStateManager instance
    """
    with patch("matcha_ml.cli.destroy.RemoteStateManager") as mock_state_manager_class:
        mock_state_manager = mock_state_manager_class.return_value
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
    runner, matcha_testing_directory, mock_remote_state_manager: MagicMock
):
    """Test destroy command when there no existing resources deployed.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
        mock_remote_state_manager (MagicMock): mock of an RemoteStateManager instance
    """
    os.chdir(matcha_testing_directory)

    mock_remote_state_manager.is_state_provisioned.return_value = False

    result = runner.invoke(app, ["destroy"])

    assert (
        "Error - resources that have not been provisioned cannot be destroyed."
        in result.stdout
    )

    mock_remote_state_manager.use_lock.assert_not_called()


def test_cli_destroy_with_nothing_provisioned(
    runner, mock_remote_state_manager: MagicMock
):
    """Test the destroy command with no resources exist at all.

    Args:
        runner (CliRunner): typer CLI runner.
        mock_remote_state_manager (MagicMock): mock of a RemoteStateManager instance.
    """
    mock_remote_state_manager.is_state_provisioned.return_value = False

    result = runner.invoke(app, ["destroy"])

    assert (
        "Error - resources that have not been provisioned cannot be destroyed."
        in result.stdout
    )
