"""Test suite to test the provision command and all its subcommands."""
import json
import os

import pytest
from typer.testing import CliRunner

from matcha_ml.cli.cli import app
from matcha_ml.cli.ui.resource_message_builders import build_resource_output

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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
        "mlflow_tracking_url": "mlflow_test_url",
        "zenml_storage_path": "zenml_test_storage_path",
        "zenml_connection_string": "zenml_test_connection_string",
        "k8s_context": "k8s_test_context",
        "azure_container_registry": "azure_container_registry",
        "azure_registry_name": "azure_registry_name",
        "zen_server_url": "zen_server_url",
        "zen_server_username": "zen_server_username",
        "zen_server_password": "zen_server_password",
        "seldon_workloads_namespace": "test_seldon_workloads_namespace",
        "seldon_base_url": "test_seldon_base_url",
        "resource_group_name": "test_resources",
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
        "mlflow_tracking_url": "mlflow_test_url",
        "zenml_storage_path": "zenml_test_storage_path",
        "zenml_connection_string": "zenml_test_connection_string",
        "k8s_context": "k8s_test_context",
        "azure_container_registry": "azure_container_registry",
        "azure_registry_name": "azure_registry_name",
        "zen_server_url": "zen_server_url",
        "zen_server_username": "zen_server_username",
        "zen_server_password": "zen_server_password",
        "seldon_workloads_namespace": "test_seldon_workloads_namespace",
        "seldon_base_url": "test_seldon_base_url",
        "resource_group_name": "test_resources",
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
    assert "Get information about the resources you've provisioned." in result.stdout


def test_cli_get_command(runner, expected_outputs: dict):
    """Test get command to print the current information about the deployed resources.

    Args:
        runner (CliRunner): typer CLI runner
        expected_outputs (dict): The expected state file.
    """
    expected = build_resource_output(expected_outputs)

    result = runner.invoke(app, ["get"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0
    assert expected in result.stdout
