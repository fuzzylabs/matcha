"""Test suite to test the run command and all it's subcommands."""
from matcha_ml import __version__
from matcha_ml.cli.cli import app


def test_cli_run_command(runner):
    """Test cli for run command."""
    # Invoke run command
    result = runner.invoke(app, ["run", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Run command." in result.stdout


def test_cli_train_command(runner):
    """Test cli for run command."""
    # Invoke run command
    result = runner.invoke(app, ["run", "train", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Run train subcommand." in result.stdout
