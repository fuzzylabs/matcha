"""Test suite for matcha cli force-unlock command."""
from unittest.mock import patch
from typer.testing import CliRunner

from matcha_ml.cli.cli import app

INTERNAL_FUNCTION_STUB = "matcha_ml.core.core"


def test_cli_force_unlock_command_help_option(runner: CliRunner) -> None:
    """Tests the --help option for the cli force-unlock command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke force-unlock command with help option
    result = runner.invoke(app, ["force-unlock", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Force unlock remote matcha state on Azure." in result.stdout


def test_cli_force_unlock_command_called(runner: CliRunner) -> None:
    """Tests the cli force-unlock command is called when running the user provides confirmation.

    Args:
        runner (CliRunner): typer CLI runner
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}.remove_state_lock") as mock_unlock:
        # Invoke force-unlock command with yes confirmation
        result = runner.invoke(app, ["force-unlock"], input="Y\n")

        # Exit code 0 means there was no error
        assert result.exit_code == 0

        # Check if unlock_state_lock function was called
        mock_unlock.assert_called_once()


def test_cli_force_unlock_command_not_called(runner: CliRunner) -> None:
    """Tests the cli force-unlock command is not called when running the user does not confirm.

    Args:
        runner (CliRunner): typer CLI runner
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}.remove_state_lock") as mock_unlock:
        # Invoke force-unlock command with no confirmation
        result = runner.invoke(app, ["force-unlock"], input="n\n")

        # Exit code 0 means there was no error
        assert result.exit_code == 0

        # Check if unlock_state_lock function was not called
        mock_unlock.assert_not_called()
