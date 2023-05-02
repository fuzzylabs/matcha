"""Test suite to test the provision command and all its subcommands."""
from typer.testing import CliRunner

from matcha_ml.cli.cli import app


def test_cli_get_command_help(runner: CliRunner):
    """Test cli for get command help.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke get command
    result = runner.invoke(app, ["get", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Get information for the provisioned resources." in result.stdout


def test_cli_get_command(runner: CliRunner):
    """Test cli for get command help.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke get command
    result = runner.invoke(app, ["get", "test_resource_name", "test_property_name"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "This is the resource name argument: test_resource_name" in result.stdout
    assert "This is the property name argument: test_property_name" in result.stdout
