"""Test suite to test the CLI."""
from typing import Iterable
from unittest.mock import MagicMock, patch

import pytest

from matcha_ml import __version__
from matcha_ml.cli.cli import app


@pytest.fixture(autouse=True)
def mock_remote_state_manager() -> Iterable[MagicMock]:
    """Mock remote state manager to have state provisioned.

    Yields:
        MagicMock: mock of an RemoteStateManager instance
    """
    with patch("matcha_ml.core.core.RemoteStateManager") as mock_state_manager_class:
        mock_state_manager = mock_state_manager_class.return_value
        yield mock_state_manager


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

    # Exit code other than 0 means there was an error in execution of program
    assert result.exit_code != 0

    # Check if error message is present in output
    assert "Error" in result.stdout
