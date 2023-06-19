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
from matcha_ml.state.matcha_state import (
    MatchaState,
    MatchaStateService,
)


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
            "cloud_azure_prefix": {
                "value": "random",
            },
            "cloud_azure_location": {
                "value": "uksouth",
            },
            "experiment_tracker_mlflow_tracking_url": {"value": "mlflow_test_url"},
            "pipeline_zenml_connection_string": {
                "value": "zenml_test_connection_string"
            },
            "pipeline_zenml_server_url": {"value": "zen_server_url"},
            "pipeline_zenml_server_password": {"value": "zen_server_password"},
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
            "connection-string": "********",
            "server-password": "********",
            "server-url": "zen_server_url",
        },
        "container-registry": {
            "flavor": "azure",
            "registry-url": "azure_container_registry",
        },
        "id": {"matcha_uuid": "matcha_id_test_value"},
    }
    return outputs


@pytest.fixture
def template_runner() -> AzureRunner:
    """Return a template runner object instance for test.

    Returns:
        AzureRunner: a AzureRunner object instance.
    """
    return AzureRunner()


def test_write_outputs_state(
    template_runner: AzureRunner,
    mock_output: Callable[[str, bool], Union[str, Dict[str, str]]],
    expected_outputs_show_sensitive: dict,
    matcha_testing_directory: str,
):
    """Test service writes the state file correctly.

    Args:
        template_runner (AzureRunner): a AzureRunner object instance
        mock_output (Callable[[str, bool], Union[str, Dict[str, str]]]): the mock output
        expected_outputs_show_sensitive (dict): expected output from terraform
        matcha_testing_directory (str): Testing directory
    """
    os.chdir(matcha_testing_directory)
    os.makedirs(os.path.dirname(MatchaStateService.matcha_state_path), exist_ok=True)
    template_runner._check_terraform_installation = MagicMock()
    template_runner._validate_terraform_config = MagicMock()
    template_runner._initialize_terraform = MagicMock()
    template_runner._apply_terraform = MagicMock()
    template_runner._show_terraform_outputs = MagicMock()
    template_runner.tfs.terraform_client.output = MagicMock(wraps=mock_output)

    with does_not_raise():
        with mock.patch("uuid.uuid4") as uuid4:
            uuid4.return_value = "matcha_id_test_value"
            template_runner.provision()
        with open(MatchaStateService.matcha_state_path) as f:
            assert json.load(f) == expected_outputs_show_sensitive


def test_show_terraform_outputs(
    template_runner: AzureRunner,
    capsys: SysCapture,
    expected_outputs_hide_sensitive: dict,
    state_file_as_object: MatchaState,
    matcha_testing_directory: str,
):
    """Test service shows the correct terraform output.

    Args:
        template_runner (AzureRunner): a AzureRunner object instance
        capsys (SysCapture): fixture to capture stdout and stderr
        expected_outputs_hide_sensitive (dict): expected output from terraform
        state_file_as_object (MatchaState): mock MatchaState dataclass object
        matcha_testing_directory (str): Testing directory
    """
    os.chdir(matcha_testing_directory)
    with does_not_raise():
        template_runner._show_terraform_outputs(state_file_as_object)
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


def test_deprovision(
    template_runner: AzureRunner,
    matcha_testing_directory: str,
    expected_outputs_show_sensitive: dict,
):
    """Test service can deprovision resources using terraform.

    Args:
        template_runner (AzureRunner): a AzureTemplateRunner object instance
        matcha_testing_directory (str): Testing directory
        expected_outputs_show_sensitive (dict): matcha.state contents before destroy is run
    """
    os.chdir(matcha_testing_directory)
    template_runner._check_terraform_installation = MagicMock()
    template_runner._check_matcha_directory_exists = MagicMock()
    template_runner._initialize_terraform = MagicMock()
    template_runner._destroy_terraform = MagicMock()
    matcha_state_file_dir = MatchaStateService.matcha_state_path

    # Create mock matcha.state file with the required contents
    os.makedirs(os.path.join(matcha_testing_directory, ".matcha", "infrastructure"))
    with open(matcha_state_file_dir, "w") as f:
        json.dump(expected_outputs_show_sensitive, f, indent=4)

    with mock.patch("typer.confirm") as mock_confirm:
        template_runner.state_file = matcha_state_file_dir
        mock_confirm.return_value = False
        template_runner._destroy_terraform.assert_not_called()

    with mock.patch("typer.confirm") as mock_confirm:
        template_runner.state_file = matcha_state_file_dir
        mock_confirm.return_value = True
        template_runner.deprovision()
        template_runner._destroy_terraform.assert_called()
