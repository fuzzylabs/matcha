"""Test suite to test the run command and all its subcommands."""
import os

import pytest

from matcha_ml import __version__
from matcha_ml.cli.cli import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def run_testing_directory(matcha_testing_directory: str):
    """A fixture for creating and removing a temporary run.py file.

    To test whether run.py is executed when the `matcha run` is used with no other commands.

    Args:
        matcha_testing_directory (str): temporary working directory

    Yields:
        run.py: a run.py temporarily containing 1 line of python code which prints "This is the run.py file".
    """

    with open(os.path.join(matcha_testing_directory, "run.py"), "w") as f:
        # f.write("print('This is the run.py file')")
        f.write("import sys\nsys.stdout.write('This is the run.py file')")

    yield matcha_testing_directory  # tests are executed at this point

    # then the run.py file is remove
    os.remove("run.py")


def test_cli_run_command(runner):
    """Test cli for run command."""
    # Invoke run command
    result = runner.invoke(app, ["run", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "The run command." in result.stdout


def test_cli_train_command(runner):
    """Test cli for run command."""
    # Invoke run command
    result = runner.invoke(app, ["run", "train", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Run train subcommand." in result.stdout


def test_cli_default_callback(runner, run_testing_directory: str, capfd):
    """Test cli for run command."""
    # Invoke run command with no option passed
    os.chdir(run_testing_directory)
    result = runner.invoke(app, ["run"])

    # capfd for file descriptor level
    captured = capfd.readouterr()

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "No commands are passed, running run.py by default." in result.stdout
    # The temporary run.py file should contain code to print the following when executed.
    assert "This is the run.py file" in captured.out
