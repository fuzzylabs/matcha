"""Test suite to test the provision command and all its subcommands."""
from matcha_ml import __version__
from matcha_ml.cli.cli import app


def test_cli_provision_command(runner):
    """Test cli for provision command."""
    # Invoke provision command
    result = runner.invoke(app, ["provision", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Provision cloud resources." in result.stdout
