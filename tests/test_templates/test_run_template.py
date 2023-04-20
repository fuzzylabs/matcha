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

from matcha_ml.services.terraform_service import TerraformConfig, TerraformService
from matcha_ml.templates.run_template import deprovision, provision


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
    terraform_test_config: TerraformConfig,
    mock_output: Callable[[str, bool], Union[str, Dict[str, str]]],
    expected_outputs: dict,
    capsys: SysCapture,
):
    """Test service can provision resources using terraform.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
        mock_output (Callable[[str, bool], Union[str, Dict[str, str]]]): the expected value based on the key
        expected_outputs (dict): the expected output from terraform
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config

    tfs.check_installation = MagicMock()
    tfs.validate_config = MagicMock()

    tfs.terraform_client.init = MagicMock(return_value=(0, "", ""))
    tfs.terraform_client.apply = MagicMock(return_value=(0, "", ""))
    tfs.terraform_client.output = MagicMock(wraps=mock_output)

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        expected_output = "You decided to cancel - if you change your mind, then run 'matcha provision' again."

        with pytest.raises(typer.Exit):
            provision(tfs)
            tfs.terraform_client.init.assert_not_called()
            tfs.terraform_client.apply.assert_not_called()
            tfs.terraform_client.output.assert_not_called()

            captured = capsys.readouterr()

            assert expected_output in captured

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True

        with does_not_raise():
            provision(tfs)
            tfs.terraform_client.init.assert_called()
            tfs.terraform_client.apply.assert_called()
            tfs.terraform_client.output.assert_called()

            with open(terraform_test_config.state_file) as f:
                assert json.load(f) == expected_outputs


def test_deprovision(
    capsys: SysCapture,
):
    """Test service can provision resources using terraform.

    Args:
        mock_output (Callable[[str, bool], Union[str, Dict[str, str]]]): the expected value based on the key
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    tfs = TerraformService()

    tfs.check_installation = MagicMock()
    tfs.check_matcha_directory_exists = MagicMock()
    tfs.check_matcha_directory_integrity = MagicMock()

    tfs.terraform_client.destroy = MagicMock(return_value=(0, "", ""))

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        expected_output = "You decided to cancel - your resources will remain active! If you change your mind, then run 'matcha destroy' again."

        with pytest.raises(typer.Exit):
            deprovision(tfs)
            tfs.terraform_client.destroy.assert_not_called()

            captured = capsys.readouterr()

            assert expected_output in captured

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True

        with does_not_raise():
            deprovision(tfs)
            tfs.terraform_client.destroy.assert_called()
