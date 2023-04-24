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


def test_initialise_terraform(capsys: SysCapture, template_runner: TemplateRunner):
    """Test if service behaves as expected when initialising Terraform.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    with mock.patch(
        "matcha_ml.templates.run_template.TemplateRunner.previous_temp_dir"
    ) as mock_previous_temp_dir:

        with mock.patch.object(mock_previous_temp_dir, "exists", return_value=True):
            expected = "has already been initialised"

            template_runner._initialise_terraform()

            captured = capsys.readouterr()

            assert expected in captured.out

        with mock.patch.object(mock_previous_temp_dir, "exists", return_value=False):
            expected = " initialised!"
            template_runner._initialise_terraform()

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
    with mock.patch(
        "matcha_ml.templates.run_template.TemplateRunner.tfs.check_matcha_directory_exists"
    ) as mock_check_matcha_directory_exists:
        mock_check_matcha_directory_exists.return_value = False
        expected = "Error, the .matcha directory does not exist"

        with pytest.raises(typer.Exit):
            template_runner._check_matcha_directory_exists()

            captured = capsys.readouterr()

            assert expected in captured.err

    with mock.patch(
        "matcha_ml.templates.run_template.TemplateRunner.tfs.check_matcha_directory_integrity"
    ) as mock_check_matcha_directory_integrity:
        mock_check_matcha_directory_integrity.return_value = False
        expected = "Error, the .matcha directory does not contain files relating to deployed resources. Please ensure you are trying to destroy resources that you have provisioned in the current working directory."

        with pytest.raises(typer.Exit):
            template_runner._check_matcha_directory_exists()

            captured = capsys.readouterr()

            assert expected in captured.err


def test_apply_terraform(capsys: SysCapture, template_runner: TemplateRunner):
    """Test if terraform applied is handled correctly during apply when provisioning resources.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (TemplateRunner): a TemplateRunner object instance
    """
    with mock.patch("matcha_ml.templates.run_template.TemplateRunner.tfs") as mock_tfs:
        mock_tfs.apply.return_value = (0, "", "")
        expected = "Your environment has been provisioned!"

        template_runner._apply_terraform()
        captured = capsys.readouterr()
        assert expected in captured.out

        mock_tfs.apply.return_value = (1, "", "Init failed")

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
    with mock.patch("matcha_ml.templates.run_template.TemplateRunner.tfs") as mock_tfs:
        template_runner.state_file = terraform_test_config.state_file
        mock_tfs.terraform_client.output = MagicMock(wraps=mock_output)

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
    with mock.patch("matcha_ml.templates.run_template.TemplateRunner.tfs") as mock_tfs:
        template_runner.state_file = terraform_test_config.state_file
        mock_tfs.terraform_client.output = MagicMock(wraps=mock_output)

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
    with mock.patch("matcha_ml.templates.run_template.TemplateRunner.tfs") as mock_tfs:
        mock_tfs.destroy.return_value = (0, "", "")
        expected = "Destroying your resources"

        template_runner._destroy_terraform()

        captured = capsys.readouterr()

        mock_tfs.destroy.assert_called()

        assert expected in captured.out

        mock_tfs.destroy.return_value = (1, "", "Init failed")

        with pytest.raises(MatchaTerraformError) as exc_info:
            template_runner._destroy_terraform()
            assert (
                str(exc_info.value)
                == "Terraform failed because of the following error: 'Destroy failed'."
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
