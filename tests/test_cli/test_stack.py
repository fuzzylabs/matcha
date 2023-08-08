"""Test suit to test the stack command and all its subcommands."""

import os

from typer.testing import CliRunner

from matcha_ml.cli.cli import app
from matcha_ml.config import MatchaConfig, MatchaConfigService

INTERNAL_FUNCTION_STUB = "matcha_ml.core"


def test_cli_stack_command_help_option(runner: CliRunner) -> None:
    """Tests the --help option for the cli stack command.

    Args:
        runner (CliRunner): typer CLI runner.
    """
    result = runner.invoke(app, ["stack", "--help"])

    assert result.exit_code == 0

    assert "Configure the stack for Matcha to provision." in result.stdout


def test_cli_stack_command_defaults_to_help(runner: CliRunner) -> None:
    """Tests the --help option for the cli stack command.

    Args:
        runner (CliRunner): typer CLI runner.
    """
    result = runner.invoke(app, ["stack"])

    assert result.exit_code == 0

    assert "Configure the stack for Matcha to provision." in result.stdout


def test_cli_stack_set_command_help_option(runner: CliRunner) -> None:
    """Tests the --help option for the cli stack set sub-command.

    Args:
        runner (CliRunner): typer CLI runner.
    """
    result = runner.invoke(app, ["stack", "set", "--help"])

    assert result.exit_code == 0

    assert "Define the stack for Matcha to provision." in result.stdout


def test_cli_stack_set_command_without_args(runner: CliRunner) -> None:
    """Tests the cli stack set sub-command.

    Args:
        runner (CliRunner): typer CLI runner.
    """
    result = runner.invoke(app, ["stack", "set"])

    assert result.exit_code == 0

    assert "Matcha default stack has been set." in result.stdout


def test_cli_stack_set_command_with_args(
    matcha_testing_directory: str, runner: CliRunner
) -> None:
    """Tests the cli stack set sub-command.

    Args:
        matcha_testing_directory (str): a temporary working directory.
        runner (CliRunner): typer CLI runner.
    """
    result = runner.invoke(app, ["stack", "set", "default"])

    assert result.exit_code == 0

    assert "Matcha default stack has been set." in result.stdout


def test_stack_set_stack_not_recognized(runner: CliRunner) -> None:
    """Tests the cli stack set sub-command behavior when an unrecognized stack name is passed.

    Args:
        runner (CliRunner): typer CLI runner.
    """
    result = runner.invoke(app, ["stack", "set", "random"])
    assert result.exit_code == 0
    assert "random is not a valid stack type" in result.stdout


def test_stack_set_file_created(
    matcha_testing_directory: str, runner: CliRunner
) -> None:
    """Test that stack_set cli command creates a config file if one doesn't exist.

    Args:
        matcha_testing_directory (str): a temporary working directory.
        runner (CliRunner): typer CLI runner.
    """
    os.chdir(matcha_testing_directory)
    result = runner.invoke(app, ["stack", "set", "llm"])
    assert result.exit_code == 0

    config = MatchaConfigService.read_matcha_config()
    assert config.to_dict() == {"stack": {"name": "LLM"}}


def test_stack_set_file_modified(
    matcha_testing_directory, mocked_matcha_config_json_object, runner: CliRunner
) -> None:
    """Test that if a config file exists, stack set cli command modifies the file.

    Args:
        matcha_testing_directory (str): temporary working directory.
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): Mocked matcha.config.json file read into Python as nested dicts.
        runner (CliRunner): typer CLI runner.
    """
    os.chdir(matcha_testing_directory)

    config = MatchaConfig.from_dict(mocked_matcha_config_json_object)
    config_dict = config.to_dict()
    MatchaConfigService.write_matcha_config(config)

    result = runner.invoke(app, ["stack", "set", "llm"])
    assert result.exit_code == 0

    new_config = MatchaConfigService.read_matcha_config()

    new_config_dict = new_config.to_dict()

    assert len(new_config_dict) == len(config_dict) + 1
    assert "stack" in new_config_dict
    assert new_config_dict["stack"]["name"] == "LLM"
    assert config_dict.items() <= new_config_dict.items()
