"""Test suite to test the CLI."""
from matcha_ml import __version__
from matcha_ml.cli.cli import app


def test_cli_no_args(runner):
    """Test cli when no option passed."""
    # Invoke no option
    result = runner.invoke(app)

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert if particular string in present in output
    assert "CLI base command for matcha" in result.stdout


def test_cli_version(runner):
    """Test cli for version option."""
    # Invoke version option
    result = runner.invoke(app, ["--version"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Check if version outptut match
    assert result.stdout.strip() == f"Matcha version: {__version__}"


def test_cli_help(runner):
    """Test cli for help option."""
    # Invoke help option
    result = runner.invoke(app, ["--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert if particular string in present in output
    assert "CLI base command for matcha" in result.stdout


def test_cli_invalid_argument(runner):
    """Test cli when invalid option is passed."""
    # Invoke invalid option dummy
    result = runner.invoke(app, ["--dummy"])

    # Exit code other than 0 means there was an error in exectuion of program
    assert result.exit_code != 0

    # Check if error message is present in output
    assert "Error" in result.stdout
