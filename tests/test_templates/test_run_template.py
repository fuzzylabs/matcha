"""Test for interacting with Terraform service."""
import os
from contextlib import nullcontext as does_not_raise
from typing import Callable, Dict, Union
from unittest import mock
from unittest.mock import MagicMock

import pytest
import typer
from _pytest.capture import SysCapture

from matcha_ml.services.terraform_service import TerraformConfig
from matcha_ml.templates.run_template import TemplateRunner


@pytest.fixture
def mock_output() -> Callable[[str, bool], Union[str, Dict[str, str]]]:
    """Fixture for mocking the terraform output.

    Returns:
        Callable[[str, bool], Union[str, Dict[str, str]]]: the expected value based on the key
    """

    def output(name: str, full_value: bool) -> str:
        terraform_outputs = {
            "mlflow-tracking-url": "mlflow-test-url",
            "zenml-storage-path": "zenml-test-storage-path",
            "zenml-connection-string": "zenml-test-connection-string",
            "k8s-context": "k8s-test-context",
            "azure-container-registry": "azure-container-registry",
            "azure-registry-name": "azure-registry-name",
            "zen-server-url": "zen-server-url",
            "zen-server-username": "zen-server-username",
            "zen-server-password": "zen-server-password",
            "seldon-workloads-namespace": "test-seldon-workloads-namespace",
            "seldon-base-url": "test-seldon-base-url",
        }
        if name not in terraform_outputs:
            raise ValueError("Unexpected input")
        if full_value:
            return terraform_outputs[name]
        else:
            return {"value": terraform_outputs[name]}

    return output


@pytest.fixture
def expected_outputs() -> dict:
    """The expected output from terraform.

    Returns:
        dict: expected output
    """
    outputs = {
        "mlflow-tracking-url": "mlflow-test-url",
        "zenml-storage-path": "zenml-test-storage-path",
        "zenml-connection-string": "zenml-test-connection-string",
        "k8s-context": "k8s-test-context",
        "azure-container-registry": "azure-container-registry",
        "azure-registry-name": "azure-registry-name",
        "zen-server-url": "zen-server-url",
        "zen-server-username": "zen-server-username",
        "zen-server-password": "zen-server-password",
        "seldon-workloads-namespace": "test-seldon-workloads-namespace",
        "seldon-base-url": "test-seldon-base-url",
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


def test_provision(
    capsys: SysCapture,
):
    """Test service can provision resources using terraform.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    template_runner = TemplateRunner()
    template_runner._check_terraform_installation = MagicMock()
    template_runner._validate_terraform_config = MagicMock()

    template_runner._initialise_terraform = MagicMock()
    template_runner._apply_terraform = MagicMock()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        expected_output = "You decided to cancel - if you change your mind, then run 'matcha provision' again."

        with pytest.raises(typer.Exit):
            template_runner.provision()
            template_runner._initialise_terraform.assert_not_called()
            template_runner._apply_terraform.assert_not_called()

            captured = capsys.readouterr()

            assert expected_output in captured

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True

        with does_not_raise():
            template_runner.provision()
            template_runner._initialise_terraform.assert_called()
            template_runner._apply_terraform.assert_called()


def test_deprovision(
    capsys: SysCapture,
):
    """Test service can deprovision resources using terraform.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    template_runner = TemplateRunner()

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
