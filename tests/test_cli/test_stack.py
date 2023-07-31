"""Test suit to test the stack command and all its subcommands."""
from unittest.mock import patch

from typer.testing import CliRunner

from matcha_ml.cli.cli import app

INTERNAL_FUNCTION_STUB = "matcha_ml.core"


def test_cli_stack_command_help_option(runner: CliRunner) -> None:
    """Tests the --help option for the cli stack command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["stack", "--help"])

    assert result.exit_code == 0

    assert "Configure the stack for Matcha to provision." in result.stdout


def test_cli_stack_command_defaults_to_help(runner: CliRunner) -> None:
    """Tests the --help option for the cli stack command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["stack"])

    assert result.exit_code == 0

    assert "Configure the stack for Matcha to provision." in result.stdout


def test_cli_stack_set_command_help_option(runner: CliRunner) -> None:
    """Tests the --help option for the cli stack set sub-command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["stack", "set", "--help"])

    assert result.exit_code == 0

    assert "Define the stack for Matcha to provision." in result.stdout


def test_cli_stack_set_command(runner: CliRunner) -> None:
    """Tests the cli stack set sub-command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}.stack_set") as mocked_stack_set:

        result = runner.invoke(app, ["stack", "set", "test_stack"])

        assert result.exit_code == 0

        mocked_stack_set.assert_called_once_with("test_stack")
