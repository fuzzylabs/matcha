"""Test for interacting with Terraform service."""
import json
import os
from contextlib import nullcontext as does_not_raise
from typing import Callable, Dict, Union
from unittest import mock
from unittest.mock import MagicMock

import pytest
import typer
from _pytest.capture import SysCapture

from matcha_ml.errors import MatchaTerraformError
from matcha_ml.services.terraform_service import TerraformConfig
from matcha_ml.templates.run_template import TemplateRunner


@pytest.fixture
def mock_output() -> Callable[[str, bool], Union[str, Dict[str, str]]]:
    """Fixture for mocking the terraform output.

    Returns:
        Callable[[str, bool], Union[str, Dict[str, str]]]: the expected value based on the key
    """

    def output() -> str:
        terraform_outputs = {
            "experiment_tracker_mlflow_tracking_url": {"value": "mlflow_test_url"},
            "pipeline_zenml_storage_path": {"value": "zenml_test_storage_path"},
            "pipeline_zenml_connection_string": {
                "value": "zenml_test_connection_string"
            },
            "orchestrator_aks_k8s_context": {"value": "k8s_test_context"},
            "container_registry_azure_registry_url": {
                "value": "azure_container_registry"
            },
            "container_registry_azure_registry_name": {"value": "azure_registry_name"},
            "pipeline_zenml_server_url": {"value": "zen_server_url"},
            "pipeline_zenml_server_username": {"value": "zen_server_username"},
            "pipeline_zenml_server_password": {"value": "zen_server_password"},
            "model_deployer_seldon_workloads_namespace": {
                "value": "test_seldon_workloads_namespace"
            },
            "model_deployer_seldon_base_url": {"value": "test_seldon_base_url"},
            "cloud_azure_resource_group_name": {"value": "test_resources"},
        }
        return terraform_outputs

    return output


@pytest.fixture
def expected_outputs() -> dict:
    """The expected output from terraform.

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
        "experiment-tracker": {
            "flavor": "mlflow",
            "tracking-url": "mlflow_test_url",
        },
        "model-deployer": {
            "flavor": "seldon",
            "base-url": "test_seldon_base_url",
            "workloads-namespace": "test_seldon_workloads_namespace",
        },
        "orchestrator": {
            "flavor": "aks",
            "k8s-context": "k8s_test_context",
        },
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


@pytest.fixture
def terraform_test_config(matcha_testing_directory: str) -> TerraformConfig:
    """Fixture for a test terraform service config pointing to a temporary directory.

    Args:
        matcha_testing_directory: temporary directory path

    Returns:
        TerraformConfig: test terraform config
    """
    infrastructure_directory = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )
    os.makedirs(infrastructure_directory, exist_ok=True)
    return TerraformConfig(
        working_dir=infrastructure_directory,
        state_file=os.path.join(infrastructure_directory, "matcha.state"),
        var_file=os.path.join(infrastructure_directory, "terraform.tfvars.json"),
    )


@pytest.fixture
def template_runner() -> TemplateRunner:
    """Return a template runner object instance for test.

    Returns:
        TemplateRunner: a TemplateRunner object instance.
    """
    return TemplateRunner()


def test_check_terraform_installation(
    capsys: SysCapture, template_runner: TemplateRunner
):
    """Test app exits when terraform is not installed.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    with mock.patch(
        "matcha_ml.templates.run_template.TemplateRunner.tfs.check_installation"
    ) as mock_check_installation:
        mock_check_installation.return_value = False
        expected = "Terraform is not installed"

        with pytest.raises(typer.Exit):
            template_runner._check_terraform_installation()
        captured = capsys.readouterr()

        assert expected in captured.err


def test_validate_terraform_config(capsys: SysCapture, template_runner: TemplateRunner):
    """Test application exits if there is no config.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    with mock.patch(
        "matcha_ml.templates.run_template.TemplateRunner.tfs.validate_config"
    ) as mock_validate_config:
        mock_validate_config.return_value = False
        expected = "The file terraform.tfvars.json was not found"

        with pytest.raises(typer.Exit):
            template_runner._validate_terraform_config()
        captured = capsys.readouterr()

        assert expected in captured.err


def test_is_approved(template_runner: TemplateRunner):
    """Test if is_approved behaves as expected based on user's input.

    Args:
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True
        assert template_runner._is_approved("provision")

        mock_confirm.return_value = False
        assert not template_runner._is_approved("provision")


def test_initialize_terraform(capsys: SysCapture, template_runner: TemplateRunner):
    """Test if service behaves as expected when initializing Terraform.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    template_runner.previous_temp_dir = MagicMock()

    with mock.patch.object(
        template_runner.previous_temp_dir, "exists", return_value=True
    ):
        expected = "has already been initialized"

        template_runner._initialize_terraform()

        captured = capsys.readouterr()

        assert expected in captured.out

    with mock.patch.object(
        template_runner.previous_temp_dir, "exists", return_value=False
    ):
        template_runner.tfs.init = MagicMock(return_value=(0, "", ""))
        expected = " initialized!"
        template_runner._initialize_terraform()

        captured = capsys.readouterr()

        assert expected in captured.out


def test_check_matcha_directory_exists(
    capsys: SysCapture, template_runner: TemplateRunner
):
    """Test if service exit as expected and print out the expected error message when required files does not exists.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    template_runner.tfs.check_matcha_directory_exists = MagicMock(return_value=False)
    template_runner.tfs.check_matcha_directory_integrity = MagicMock(return_value=False)

    with pytest.raises(typer.Exit):
        expected = "Error, the .matcha directory does not exist"
        template_runner._check_matcha_directory_exists()

        captured = capsys.readouterr()

        assert expected in captured.err

    with pytest.raises(typer.Exit):
        expected = "Error, the .matcha directory does not contain files relating to deployed resources. Please ensure you are trying to destroy resources that you have provisioned in the current working directory."
        template_runner._check_matcha_directory_exists()

        captured = capsys.readouterr()

        assert expected in captured.err


def test_apply_terraform(capsys: SysCapture, template_runner: TemplateRunner):
    """Test if terraform applied is handled correctly during apply when provisioning resources.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    template_runner.tfs.apply = MagicMock(return_value=(0, "", ""))
    expected = "Your environment has been provisioned!"

    template_runner._apply_terraform()
    captured = capsys.readouterr()

    assert expected in captured.out

    template_runner.tfs.apply = MagicMock(return_value=(1, "", "Apply failed"))

    with pytest.raises(MatchaTerraformError) as exc_info:
        template_runner._apply_terraform()
        assert (
            str(exc_info.value)
            == "Terraform failed because of the following error: 'Apply failed'."
        )


def test_write_outputs_state(
    template_runner: TemplateRunner,
    terraform_test_config: TerraformConfig,
    mock_output: Callable[[str, bool], Union[str, Dict[str, str]]],
    expected_outputs,
):
    """Test service writes the state file correctly.

    Args:
        template_runner (TemplateRunner): a TemplateRunner object instance
        terraform_test_config (TerraformConfig): test terraform service config
        mock_output (Callable[[str, bool], Union[str, Dict[str, str]]]): the mock output
        expected_outputs (dict): expected output from terraform
    """
    template_runner.state_file = terraform_test_config.state_file
    template_runner.tfs.terraform_client.output = MagicMock(wraps=mock_output)

    with does_not_raise():
        template_runner._write_outputs_state()
        with open(terraform_test_config.state_file) as f:
            assert json.load(f) == expected_outputs


def test_show_terraform_outputs(
    template_runner: TemplateRunner,
    terraform_test_config: TerraformConfig,
    capsys: SysCapture,
    mock_output: Callable[[str, bool], Union[str, Dict[str, str]]],
    expected_outputs: dict,
):
    """Test service shows the correct terraform output.

    Args:
        template_runner (TemplateRunner): a TemplateRunner object instance
        terraform_test_config (TerraformConfig): test terraform service config
        capsys (SysCapture): fixture to capture stdout and stderr
        mock_output (Callable[[str, bool], Union[str, Dict[str, str]]]): the mock output
        expected_outputs (dict): expected output from terraform
    """
    template_runner.state_file = terraform_test_config.state_file
    template_runner.tfs.terraform_client.output = MagicMock(wraps=mock_output)

    with does_not_raise():
        template_runner._show_terraform_outputs()
        captured = capsys.readouterr()

        for output in expected_outputs:
            assert output in captured.out


def test_destroy_terraform(capsys: SysCapture, template_runner: TemplateRunner):
    """Test if terraform exception is captured when performing deprovision.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    template_runner.tfs.destroy = MagicMock(return_value=(0, "", ""))

    expected = "Destroying your resources"

    template_runner._destroy_terraform()

    captured = capsys.readouterr()

    template_runner.tfs.destroy.assert_called()

    assert expected in captured.out

    template_runner.tfs.destroy = MagicMock(return_value=(1, "", "Init failed"))

    with pytest.raises(MatchaTerraformError) as exc_info:
        template_runner._destroy_terraform()
        assert (
            str(exc_info.value)
            == "Terraform failed because of the following error: 'Destroy failed'."
        )


def test_provision(capsys: SysCapture, template_runner: TemplateRunner):
    """Test service can provision resources using terraform.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    template_runner._check_terraform_installation = MagicMock()
    template_runner._validate_terraform_config = MagicMock()
    template_runner._initialize_terraform = MagicMock()
    template_runner._apply_terraform = MagicMock()
    template_runner._show_terraform_outputs = MagicMock()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        expected_output = "You decided to cancel - if you change your mind, then run 'matcha provision' again."

        with pytest.raises(typer.Exit):
            template_runner.provision()
            template_runner._initialize_terraform.assert_not_called()
            template_runner._apply_terraform.assert_not_called()

            captured = capsys.readouterr()

            assert expected_output in captured

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True

        with does_not_raise():
            template_runner.provision()
            template_runner._initialize_terraform.assert_called()
            template_runner._apply_terraform.assert_called()


def test_deprovision(capsys: SysCapture, template_runner: TemplateRunner):
    """Test service can deprovision resources using terraform.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    template_runner._check_terraform_installation = MagicMock()
    template_runner._check_matcha_directory_exists = MagicMock()
    template_runner._destroy_terraform = MagicMock()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        expected_output = "You decided to cancel - your resources will remain active! If you change your mind, then run 'matcha destroy' again."

        with pytest.raises(typer.Exit):
            template_runner.deprovision()
            template_runner._destroy_terraform.assert_not_called()

            captured = capsys.readouterr()

            assert expected_output in captured

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True

        with does_not_raise():
            template_runner.deprovision()
            template_runner._destroy_terraform.assert_called()
