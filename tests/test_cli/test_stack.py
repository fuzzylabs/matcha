"""Test suit to test the stack command and all its subcommands."""
from unittest.mock import patch

from typer.testing import CliRunner

from matcha_ml.cli.cli import app

INTERNAL_FUNCTION_STUB = "matcha_ml.core"


def test_cli_stack_command_help_option(runner: CliRunner) -> None:
    """Tests the --help option for the cli analytics command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke analytics command with help option
    result = runner.invoke(app, ["stack", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Configure the stack for Matcha to provision." in result.stdout


def test_cli_stack_command_defaults_to_help(runner: CliRunner) -> None:
    """Tests the --help option for the cli analytics command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke analytics command with help option
    result = runner.invoke(app, ["stack"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Configure the stack for Matcha to provision." in result.stdout


def test_cli_stack_set_command_help_option(runner: CliRunner) -> None:
    """Tests the --help option for the cli analytics command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke analytics command with help option
    result = runner.invoke(app, ["stack", "set", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Define the stack for Matcha to provision." in result.stdout


def test_cli_stack_set_command(runner: CliRunner) -> None:
    """Tests the cli stack set command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}.stack_set") as mocked_stack_set:

        # Invoke analytics command and opt-in sub-command
        result = runner.invoke(app, ["stack", "set", "test_stack"])

        # Exit code 0 means there was no error
        assert result.exit_code == 0

        # Assert core.analytics_opt_out is called
        mocked_stack_set.assert_called_once_with("test_stack")
