"""Test suite to test the provision command and all its subcommands."""
import json
import os

import pytest
import yaml
from typer.testing import CliRunner

from matcha_ml.cli.cli import app


@pytest.fixture(autouse=True)
def mock_state_file(matcha_testing_directory: str):
    """A fixture for mocking a test state file in the test directory.

    Args:
        matcha_testing_directory (str): the test directory
    """
    os.chdir(matcha_testing_directory)

    matcha_infrastructure_dir = os.path.join(".matcha", "infrastructure")
    os.makedirs(matcha_infrastructure_dir)

    state_file_resources = {
        "cloud": {"flavor": "azure", "resource-group-name": "test_resources"},
        "container-registry": {
            "flavor": "azure",
            "registry-name": "azure_registry_name",
            "registry-url": "azure_container_registry",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
    }

    with open(os.path.join(matcha_infrastructure_dir, "matcha.state"), "w") as f:
        json.dump(state_file_resources, f)


@pytest.fixture
def expected_outputs() -> dict:
    """The expected state file initialized.

    Returns:
        dict: expected output
    """
    outputs = {
        "cloud": {"flavor": "azure", "resource-group-name": "test_resources"},
        "container-registry": {
            "flavor": "azure",
            "registry-name": "azure_registry_name",
            "registry-url": "azure_container_registry",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
    }

    return outputs


def test_cli_get_command_help(runner: CliRunner):
    """Test cli for get command help.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke get command
    result = runner.invoke(app, ["get", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Get information for the provisioned resources." in result.stdout


def test_cli_get_command_with_no_state_file(runner: CliRunner):
    """Test cli for get command when the state file does not exist.

    Args:
        runner (CliRunner): typer CLI runner
    """
    state_file_path = os.path.join(".matcha", "infrastructure", "matcha.state")
    os.remove(state_file_path)

    # Invoke get command
    result = runner.invoke(app, ["get"])

    assert result.exit_code == 0
    assert "Error: matcha.state file does not exist at" in str(result.stdout)


def test_cli_get_command_with_resource(runner: CliRunner):
    """Test cli for get command with a specified resource.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke get command
    result = runner.invoke(app, ["get", "experiment-tracker"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    expected_output_lines = [
        "Below are the resources provisioned.",
        "Experiment tracker",
        "- flavor: mlflow",
        "- tracking-url: mlflow_test_url",
    ]

    for line in expected_output_lines:
        assert line in result.stdout


def test_cli_get_command_with_invalid_resource_name(runner: CliRunner):
    """Test cli for get command with a resource name that does not exist in the state file.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke get command
    result = runner.invoke(app, ["get", "does-not-exist"])

    assert result.exit_code == 0
    assert (
        "Error - a resource type with the name 'does-not-exist' does not exist."
        in result.stdout
    )


def test_cli_get_command_with_resource_and_property(runner: CliRunner):
    """Test cli for get command with a specified resource and resource property.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke get command
    result = runner.invoke(app, ["get", "experiment-tracker", "tracking-url"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    expected_output_lines = [
        "Below are the resources provisioned.",
        "Experiment tracker",
        "- tracking-url: mlflow_test_url",
    ]

    for line in expected_output_lines:
        assert line in result.stdout


def test_cli_get_command_with_resource_and_property_json(runner: CliRunner):
    """Test cli for get command with a specified resource and resource property in the JSON output format.

    Args:
        runner (CliRunner): typer CLI runner
    """
    expected_output = json.dumps(
        {"experiment-tracker": {"tracking-url": "mlflow_test_url"}}, indent=2
    )

    # Invoke get command
    result = runner.invoke(
        app, ["get", "experiment-tracker", "tracking-url", "--output", "json"]
    )

    # Exit code 0 means there was no error
    assert result.exit_code == 0
    # Assert JSON is present and correct in cli output
    assert expected_output in result.stdout


def test_cli_get_command_json(runner: CliRunner, expected_outputs: dict):
    """Test cli get command default in JSON output.

    Args:
        runner (CliRunner): typer CLI runner
        expected_outputs (dict): expected output as a dict.
    """
    expected_output = json.dumps(expected_outputs, indent=2)

    # Invoke get command
    result = runner.invoke(app, ["get", "--output", "json"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0
    # Assert JSON is present and correct in cli output
    assert expected_output in result.stdout


def test_cli_get_command_yaml(runner: CliRunner, expected_outputs: dict):
    """Test cli get command default in YAML output.

    Args:
        runner (CliRunner): typer CLI runner
        expected_outputs (dict): expected output as a dict
    """
    expected_output = yaml.dump(expected_outputs, indent=2)

    # Invoke get command
    result = runner.invoke(app, ["get", "--output", "yaml"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0
    # Assert JSON is present and correct in cli output
    assert expected_output in result.stdout
