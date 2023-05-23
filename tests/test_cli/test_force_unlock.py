"""Test suite for matcha cli force-unlock command."""
from typer.testing import CliRunner

from matcha_ml.cli.cli import app


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
    assert (
        "Force unlock lock on remote matcha state on azure."
        in result.stdout
    )