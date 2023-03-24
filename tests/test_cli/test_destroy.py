"""Test suite to test the destroy command and all its subcommands."""
from matcha_ml.cli.cli import app


def test_cli_destroy_command_help(runner):
    """Test cli for provision command help.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke provision command
    result = runner.invoke(app, ["destroy", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Destroy the provisioned cloud resources." in result.stdout
