"""Test suite to test the provision command and all its subcommands."""
import json
import os

import pytest
import yaml
from typer.testing import CliRunner

from matcha_ml.cli.cli import app
from matcha_ml.cli.get import get_resources
from matcha_ml.services.matcha_state import MatchaStateService


@pytest.fixture
def matcha_state_service() -> MatchaStateService:
    """Return a template runner object instance for test.

    Returns:
        TemplateRunner: a TemplateRunner object instance.
    """
    return MatchaStateService()


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
        "model-deployer": {
            "flavor": "seldon",
            "base-url": "test_seldon_base_url",
            "workloads-namespace": "test_seldon_workloads_namespace",
        },
        "orchestrator": {"flavor": "aks", "k8s-context": "k8s_test_context"},
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "zenml_test_connection_string",
            "server-password": "zen_server_password",
            "server-url": "zen_server_url",
            "server-username": "zen_server_username",
            "storage-path": "zenml_test_storage_path",
        },
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
        "model-deployer": {
            "flavor": "seldon",
            "base-url": "test_seldon_base_url",
            "workloads-namespace": "test_seldon_workloads_namespace",
        },
        "orchestrator": {"flavor": "aks", "k8s-context": "k8s_test_context"},
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "zenml_test_connection_string",
            "server-password": "zen_server_password",
            "server-url": "zen_server_url",
            "server-username": "zen_server_username",
            "storage-path": "zenml_test_storage_path",
        },
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


def test_get_resources(
    matcha_state_service: MatchaStateService, expected_outputs: dict
):
    """Test get resources function with no resource specified.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
        expected_outputs (dict): The expected output from the matcha state file.
    """
    assert matcha_state_service.check_state_file_exists()
    assert expected_outputs == get_resources(None, None, matcha_state_service)


def test_get_resources_with_resource_name(matcha_state_service: MatchaStateService):
    """Test get resources function with resource name specified.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
    """
    expected_output = {
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"}
    }

    assert matcha_state_service.check_state_file_exists()
    assert expected_output == get_resources(
        "experiment-tracker", None, matcha_state_service
    )


def test_get_resources_with_resource_name_and_property_name(
    matcha_state_service: MatchaStateService,
):
    """Test get resources function with resource name and resource property specified.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
    """
    expected_output = {"experiment-tracker": {"tracking-url": "mlflow_test_url"}}

    assert matcha_state_service.check_state_file_exists()
    assert expected_output == get_resources(
        "experiment-tracker", "tracking-url", matcha_state_service
    )
