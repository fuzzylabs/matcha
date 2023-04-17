"""Test suite to test the run command and all its subcommands."""
import os

import pytest
from pytest import CaptureFixture
from typer.testing import CliRunner

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
        f.write("print('This is the run.py file')")

    yield matcha_testing_directory  # tests are executed at this point

    # then the run.py file is remove
    os.remove("run.py")


def test_cli_run_command(runner: CliRunner):
    """Test cli for run command.

    Args:
        runner (CliRunner): runner is what will "invoke" a command line application
    """
    # Invoke run command
    result = runner.invoke(app, ["run", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "The run command." in result.stdout


def test_cli_train_command(runner: CliRunner):
    """Test cli for train command.

    Args:
        runner (CliRunner): runner is what will "invoke" a command line application
    """
    # Invoke run command
    result = runner.invoke(app, ["run", "train", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Run train subcommand." in result.stdout
    
    
def test_cli_deploy_command_script_does_not_exist(runner: CliRunner):
    """Test that the FileNotFoundError is handled correctly when run.py does not exist.
    
    Args:
        runner (CliRunner): runner is what will "invoke" a command line application
    """
    # Invoke run command
    result = runner.invoke(app, ["run", "deploy"])

    # Exit code other than 0 means there was an error in execution of program
    assert result.exit_code != 0

    # Check if exception is FileNotFoundError 
    assert type(result.exception) == type(FileNotFoundError())


def test_cli_default_callback(
    runner: CliRunner, run_testing_directory: str, capfd: CaptureFixture
):
    """Test cli default run command.

    Args:
        runner (CliRunner): runner is what will "invoke" a command line application
        run_testing_directory (str): directory of the temp run.py created
        capfd (CaptureFixture): capture any output sent to stdout and stderr
    """
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
