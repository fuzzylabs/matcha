"""Test suit to test the stack command and all its subcommands."""

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


def test_cli_stack_set_command_without_args(runner: CliRunner) -> None:
    """Tests the cli stack set sub-command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["stack", "set"])

    assert result.exit_code == 0

    assert "Matcha default stack has been set." in result.stdout


def test_cli_stack_set_command_with_args(runner: CliRunner) -> None:
    """Tests the cli stack set sub-command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["stack", "set", "default"])

    assert result.exit_code == 0

    assert "Matcha default stack has been set." in result.stdout


def test_stack_set_stack_not_recognized(runner: CliRunner) -> None:
    """Tests the cli stack set sub-command behavior when an unrecognized stack name is passed.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["stack", "set", "random"])
    assert result.exit_code == 0
    assert "random is not a valid stack type" in result.stdout


def test_stack_set_file_created() -> None:
    pass


def test_stack_set_file_modified() -> None:
    pass