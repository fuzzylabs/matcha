"""Test for testing AzureRunner class."""
import json
import os
from contextlib import nullcontext as does_not_raise
from typing import Callable, Dict, Union
from unittest import mock
from unittest.mock import MagicMock

import pytest
from _pytest.capture import SysCapture

from matcha_ml.runners import AzureRunner
from matcha_ml.services.terraform_service import TerraformConfig


@pytest.fixture
def mock_output() -> Callable[[str, bool], Union[str, Dict[str, str]]]:
    """Fixture for mocking the terraform output.

    Returns:
        Callable[[str, bool], Union[str, Dict[str, str]]]: the expected value based on the key
    """

    def output() -> str:
        terraform_outputs = {
            "cloud_azure_resource_group_name": {
                "value": "random-resources",
            },
            "experiment_tracker_mlflow_tracking_url": {"value": "mlflow_test_url"},
            "pipeline_zenml_connection_string": {
                "value": "zenml_test_connection_string"
            },
            "pipeline_zenml_server_url": {"value": "zen_server_url"},
            "pipeline_zenml_server_password": {"value": "zen_server_password"},
            "orchestrator_aks_k8s_context": {"value": "k8s_test_context"},
            "container_registry_azure_registry_url": {
                "value": "azure_container_registry"
            },
        }
        return terraform_outputs

    return output


@pytest.fixture
def expected_outputs_show_sensitive() -> Dict[str, Dict[str, str]]:
    """The expected output from terraform.

    Returns:
        dict: expected output
    """
    outputs = {
        "cloud": {
            "flavor": "azure",
            "resource-group-name": "random-resources",
            "location": "uksouth",
            "prefix": "random",
        },
        "experiment-tracker": {
            "flavor": "mlflow",
            "tracking-url": "mlflow_test_url",
        },
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "zenml_test_connection_string",
            "server-password": "zen_server_password",
            "server-url": "zen_server_url",
        },
        "orchestrator": {
            "flavor": "aks",
            "k8s-context": "k8s_test_context",
        },
        "container-registry": {
            "flavor": "azure",
            "registry-url": "azure_container_registry",
        },
        "id": {"matcha_uuid": "matcha_id_test_value"},
    }

    return outputs


@pytest.fixture
def expected_outputs_hide_sensitive() -> dict:
    """The expected output from terraform.

    Returns:
        dict: expected output
    """
    outputs = {
        "experiment-tracker": {
            "flavor": "mlflow",
            "tracking-url": "mlflow_test_url",
        },
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "********",
            "server-password": "********",
            "server-url": "zen_server_url",
        },
        "orchestrator": {
            "flavor": "aks",
            "k8s-context": "k8s_test_context",
        },
        "container-registry": {
            "flavor": "azure",
            "registry-url": "azure_container_registry",
        },
        "id": {"matcha_uuid": "matcha_id_test_value"},
        "prefix": "random",
        "location": "uksouth",
    }
    return outputs


@pytest.fixture
def terraform_test_config(matcha_testing_directory: str) -> TerraformConfig:
    """Fixture for a test terraform service config pointing to a temporary directory.

    Args:
        matcha_testing_directory: temporary directory path

    Returns:
        TerraformConfig: test terraform config
    """
    infrastructure_directory = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "resources"
    )
    os.makedirs(infrastructure_directory, exist_ok=True)

    # Create a dummy matcha state file
    matcha_state_file = os.path.join(infrastructure_directory, "matcha.state")
    dummy_data = {"cloud": {"prefix": "random", "location": "uksouth"}}
    with open(matcha_state_file, "w") as fp:
        json.dump(dummy_data, fp)

    return TerraformConfig(working_dir=infrastructure_directory)


@pytest.fixture
def template_runner() -> AzureRunner:
    """Return a template runner object instance for test.

    Returns:
        AzureRunner: a AzureRunner object instance.
    """
    return AzureRunner()


def test_write_outputs_state(
    template_runner: AzureRunner,
    terraform_test_config: TerraformConfig,
    mock_output: Callable[[str, bool], Union[str, Dict[str, str]]],
    expected_outputs_show_sensitive: dict,
):
    """Test service writes the state file correctly.

    Args:
        template_runner (AzureRunner): a AzureRunner object instance
        terraform_test_config (TerraformConfig): test terraform service config
        mock_output (Callable[[str, bool], Union[str, Dict[str, str]]]): the mock output
        expected_outputs_show_sensitive (dict): expected output from terraform
    """
    template_runner.state_file = terraform_test_config.state_file
    template_runner.tfs.terraform_client.output = MagicMock(wraps=mock_output)

    with does_not_raise():
        with mock.patch("uuid.uuid4") as uuid4:
            uuid4.return_value = "matcha_id_test_value"
            template_runner._write_outputs_state()
        with open(terraform_test_config.state_file) as f:
            assert json.load(f) == expected_outputs_show_sensitive


def test_show_terraform_outputs(
    template_runner: AzureRunner,
    terraform_test_config: TerraformConfig,
    capsys: SysCapture,
    mock_output: Callable[[str, bool], Union[str, Dict[str, str]]],
    expected_outputs_hide_sensitive: dict,
):
    """Test service shows the correct terraform output.

    Args:
        template_runner (AzureRunner): a AzureRunner object instance
        terraform_test_config (TerraformConfig): test terraform service config
        capsys (SysCapture): fixture to capture stdout and stderr
        mock_output (Callable[[str, bool], Union[str, Dict[str, str]]]): the mock output
        expected_outputs_hide_sensitive (dict): expected output from terraform
    """
    template_runner.state_file = terraform_test_config.state_file
    template_runner.tfs.terraform_client.output = MagicMock(wraps=mock_output)

    with does_not_raise():
        template_runner._show_terraform_outputs()
        captured = capsys.readouterr()

        for output in expected_outputs_hide_sensitive:
            assert output in captured.out


def test_provision(template_runner: AzureRunner):
    """Test service can provision resources using terraform.

    Args:
        template_runner (AzureRunner): a AzureRunner object instance
    """
    template_runner._check_terraform_installation = MagicMock()
    template_runner._validate_terraform_config = MagicMock()
    template_runner._initialize_terraform = MagicMock()
    template_runner._apply_terraform = MagicMock()
    template_runner._show_terraform_outputs = MagicMock()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        template_runner._initialize_terraform.assert_not_called()
        template_runner._apply_terraform.assert_not_called()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True
        template_runner.provision()
        template_runner._initialize_terraform.assert_called()
        template_runner._apply_terraform.assert_called()


def test_deprovision(template_runner: AzureRunner):
    """Test service can deprovision resources using terraform.

    Args:
        template_runner (AzureRunner): a AzureRunner object instance
    """
    template_runner._check_terraform_installation = MagicMock()
    template_runner._check_matcha_directory_exists = MagicMock()
    template_runner._destroy_terraform = MagicMock()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        template_runner._destroy_terraform.assert_not_called()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True
        template_runner.deprovision()
        template_runner._destroy_terraform.assert_called()
