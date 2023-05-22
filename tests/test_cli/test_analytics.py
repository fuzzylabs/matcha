"""Test suite testing command for opting out of analytics."""
from unittest.mock import patch

from typer.testing import CliRunner

from matcha_ml.cli.cli import app

INTERNAL_FUNCTION_STUB = "matcha_ml.core.core"


def test_cli_analytics_command_help_option(runner: CliRunner) -> None:
    """Tests the --help option for the cli analytics command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke analytics command with help option
    result = runner.invoke(app, ["analytics", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert (
        "Enable or disable the collection of anonymous usage data (enabled by default)."
        in result.stdout
    )


def test_cli_analytics_command_defaults_to_help(runner: CliRunner) -> None:
    """Tests the cli analytics command defaults to the --help option when no sub-commands, options or arguments are passed.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke analytics command with no option
    result = runner.invoke(app, ["analytics"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert (
        "Enable or disable the collection of anonymous usage data (enabled by default)."
        in result.stdout
    )


def test_cli_analytics_opt_in_command(runner: CliRunner) -> None:
    """Tests the cli functionality for the opt-in command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}.analytics_opt_in") as mocked_opt_in:

        # Invoke analytics command and opt-in sub-command
        result = runner.invoke(app, ["analytics", "opt-in"])

        # Exit code 0 means there was no error
        assert result.exit_code == 0

        #  Assert string in present in cli output
        assert (
            "Thank you for enabling data collection, this helps us improve matcha and anonymously understand how people are using the tool."
            in result.stdout
        )

        # Assert core.analytics_opt_out is called
        mocked_opt_in.assert_called_once()


def test_cli_analytics_opt_out_command(runner: CliRunner) -> None:
    """Tests the cli functionality for the opt-out command.

    Args:
        runner (CliRunner): typer CLI runner
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}.analytics_opt_out") as mocked_opt_out:

        # Invoke analytics command and opt-in sub-command
        result = runner.invoke(app, ["analytics", "opt-out"])

        # Exit code 0 means there was no error
        assert result.exit_code == 0

        #  Assert string in present in cli output
        assert (
            "Data collection has been turned off and no data will be collected - you can turn this back on by running the command: 'matcha analytics opt-in'."
            in result.stdout
        )

        # Assert core.analytics_opt_out is called
        mocked_opt_out.assert_called_once()
