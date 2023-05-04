"""Test suite to test the provision command and all its subcommands."""
import json
import os
from typing import Dict

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
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "zenml_test_connection_string",
            "server-password": "zen_server_password",
            "server-url": "zen_server_url",
        },
        "container-registry": {
            "flavor": "azure",
            "registry-url": "azure_container_registry",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
        "orchestrator": {
            "flavor": "aks",
            "k8s-context": "k8s_test_context",
        },
    }

    with open(os.path.join(matcha_infrastructure_dir, "matcha.state"), "w") as f:
        json.dump(state_file_resources, f)


@pytest.fixture
def expected_outputs_hide_sensitive() -> Dict[str, Dict[str, str]]:
    """The expected output from terraform.

    Returns:
        dict: expected output
    """
    outputs = {
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "********",
            "server-password": "********",
            "server-url": "zen_server_url",
        },
        "container-registry": {
            "flavor": "azure",
            "registry-url": "azure_container_registry",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
        "orchestrator": {"flavor": "aks", "k8s-context": "k8s_test_context"},
    }
    return outputs


@pytest.fixture
def expected_outputs_show_sensitive() -> Dict[str, Dict[str, str]]:
    """The expected output from terraform.

    Returns:
        dict: expected output
    """
    outputs = {
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "********",
            "server-password": "********",
            "server-url": "zen_server_url",
        },
        "container-registry": {
            "flavor": "azure",
            "registry-url": "azure_container_registry",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
        "orchestrator": {"flavor": "aks", "k8s-context": "k8s_test_context"},
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


def test_cli_get_command_hide_sensitive(runner: CliRunner):
    """Test cli get command when getting all resources with no `show-sensitive` option specified.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["get"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    expected_output_lines = [
        "Pipeline",
        "- flavor: zenml",
        "- connection-string: ********",
        "- server-password: *******",
        "- server-url: zen_server_url",
        "Container registry",
        "- flavor: azure",
        "- registry-url: azure_container_registry",
        "Experiment tracker",
        "- flavor: mlflow",
        "- tracking-url: mlflow_test_url",
        "Orchestrator",
        "- flavor: aks",
        "- k8s-context: k8s_test_context",
    ]

    for line in expected_output_lines:
        assert line in result.stdout


def test_cli_get_command_show_sensitive(runner: CliRunner):
    """Test cli for get command when getting all resources with show-sensitive` option specified.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["get", "--show-sensitive"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    expected_output_lines = [
        "Pipeline",
        "- flavor: zenml",
        "- connection-string: zenml_test_connection_string",
        "- server-password: zen_server_password",
        "- server-url: zen_server_url",
        "Container registry",
        "- flavor: azure",
        "- registry-url: azure_container_registry",
        "Experiment tracker",
        "- flavor: mlflow",
        "- tracking-url: mlflow_test_url",
        "Orchestrator",
        "- flavor: aks",
        "- k8s-context: k8s_test_context",
    ]

    for line in expected_output_lines:
        assert line in result.stdout


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


def test_cli_get_command_json_no_show_sensitive(
    runner: CliRunner, expected_outputs_hide_sensitive: dict
):
    """Test cli get command default in JSON output with no `show-sensitive` option specified.

    Args:
        runner (CliRunner): typer CLI runner
        expected_outputs_hide_sensitive (dict): expected output as a dict.
    """
    expected_output = json.dumps(expected_outputs_hide_sensitive, indent=2)

    # Invoke get command
    result = runner.invoke(app, ["get", "--output", "json"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0
    # Assert JSON is present and correct in cli output
    assert expected_output in result.stdout


def test_cli_get_command_yaml_no_show_sensitive(
    runner: CliRunner, expected_outputs_hide_sensitive: dict
):
    """Test cli get command default in YAML output with no `show-sensitive` option specified..

    Args:
        runner (CliRunner): typer CLI runner
        expected_outputs_hide_sensitive (dict): expected output as a dict
    """
    expected_output = yaml.dump(expected_outputs_hide_sensitive, indent=2)

    # Invoke get command
    result = runner.invoke(app, ["get", "--output", "yaml"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0
    # Assert JSON is present and correct in cli output
    assert expected_output in result.stdout


def test_cli_get_command_json_show_sensitive(
    runner: CliRunner, expected_outputs_show_sensitive: dict
):
    """Test cli get command default in JSON output with `show-sensitive` option specified..

    Args:
        runner (CliRunner): typer CLI runner
        expected_outputs_show_sensitive (dict): expected output as a dict.
    """
    expected_output = json.dumps(expected_outputs_show_sensitive, indent=2)

    # Invoke get command
    result = runner.invoke(app, ["get", "--output", "json"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0
    # Assert JSON is present and correct in cli output
    assert expected_output in result.stdout


def test_cli_get_command_yaml_show_sensitive(
    runner: CliRunner, expected_outputs_show_sensitive: dict
):
    """Test cli get command default in YAML output with `show-sensitive` option specified..

    Args:
        runner (CliRunner): typer CLI runner
        expected_outputs_show_sensitive (dict): expected output as a dict
    """
    expected_output = yaml.dump(expected_outputs_show_sensitive, indent=2)

    # Invoke get command
    result = runner.invoke(app, ["get", "--output", "yaml"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0
    # Assert JSON is present and correct in cli output
    assert expected_output in result.stdout


def test_cli_get_command_no_show_sensitive_with_sensitive_resource(runner: CliRunner):
    """Test cli get command for when getting resource with sensitive value with no `show-sensitive` option specified.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["get", "pipeline"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # # Assert string is present in cli output
    expected_output_lines = [
        "Pipeline",
        "- flavor: zenml",
        "- connection-string: ********",
        "- server-password: ********",
        "- server-url: zen_server_url",
    ]

    for line in expected_output_lines:
        assert line in result.stdout


def test_cli_get_command_show_sensitive_with_resource(runner: CliRunner):
    """Test cli get command for when getting resource with sensitive value with `show-sensitive` option specified.

    Args:
        runner (CliRunner): typer CLI runner
    """
    result = runner.invoke(app, ["get", "pipeline", "--show-sensitive"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # # Assert string is present in cli output
    expected_output_lines = [
        "Pipeline",
        "- flavor: zenml",
        "- connection-string: zenml_test_connection_string",
        "- server-password: zen_server_password",
        "- server-url: zen_server_url",
    ]

    for line in expected_output_lines:
        assert line in result.stdout
