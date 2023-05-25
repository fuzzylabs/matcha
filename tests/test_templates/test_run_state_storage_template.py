"""Test for interacting with terraform service to run the state storage template."""
import os
from typing import Callable, Dict, Union
from unittest import mock
from unittest.mock import MagicMock

import pytest
import typer
from _pytest.capture import SysCapture

from matcha_ml.errors import MatchaTerraformError
from matcha_ml.services.terraform_service import TerraformConfig
from matcha_ml.templates.state_storage_template.run_state_storage_template import (
    StateStorageTemplateRunner,
)


@pytest.fixture
def mock_output() -> Callable[[str, bool], Union[str, Dict[str, str]]]:
    """Fixture for mocking the terraform output.

    Returns:
        Callable[[str, bool], Union[str, Dict[str, str]]]: the expected value based on the key
    """

    def output() -> str:
        terraform_outputs = {
            "remote_state_storage_account_name": {"value": "test_account_name"},
            "remote_state_storage_container_name": {"value": "test_container_name"},
        }
        return terraform_outputs

    return output


@pytest.fixture
def expected_bucket_config() -> dict:
    """The expected output generated for the config file when a state bucket is provisioned.

    Returns:
        dict: the expected output
    """
    outputs = {
        "remote_state_storage": {
            "account_name": "test_account_name",
            "container_name": "test_container_name",
        }
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
        matcha_testing_directory, ".matcha", "infrastructure", "remote_state_storage"
    )
    os.makedirs(infrastructure_directory, exist_ok=True)

    return TerraformConfig(working_dir=infrastructure_directory)


@pytest.fixture
def template_runner() -> StateStorageTemplateRunner:
    """Return a template runner object instance for test.

    Returns:
        StateStorageTemplateRunner: a StateStorageTemplateRunner object instance.
    """
    return StateStorageTemplateRunner()


def test_check_terraform_installation(
    capsys: SysCapture, template_runner: StateStorageTemplateRunner
):
    """Test app exits when terraform is not installed.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (StateStorageTemplateRunner): a StateStorageTemplateRunner object instance
    """
    with mock.patch(
        "matcha_ml.templates.state_storage_template.run_state_storage_template.StateStorageTemplateRunner.tfs.check_installation"
    ) as mock_check_installation:
        mock_check_installation.return_value = False
        expected = "Terraform is not installed"

        with pytest.raises(typer.Exit):
            template_runner._check_terraform_installation()
        captured = capsys.readouterr()

        assert expected in captured.err


def test_validate_terraform_config(
    capsys: SysCapture, template_runner: StateStorageTemplateRunner
):
    """Test application exits if there is no config.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (StateStorageTemplateRunner): a StateStorageTemplateRunner object instance
    """
    with mock.patch(
        "matcha_ml.templates.state_storage_template.run_state_storage_template.StateStorageTemplateRunner.tfs.validate_config"
    ) as mock_validate_config:
        mock_validate_config.return_value = False
        expected = "The file terraform.tfvars.json was not found"

        with pytest.raises(typer.Exit):
            template_runner._validate_terraform_config()
        captured = capsys.readouterr()

        assert expected in captured.err


def test_initialize_terraform(
    capsys: SysCapture, template_runner: StateStorageTemplateRunner
):
    """Test if service behaves as expected when initializing Terraform.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (StateStorageTemplateRunner): a StateStorageTemplateRunner object instance
    """
    expected = "Remote state management initialized!"

    template_runner.tfs.init = MagicMock(return_value=(0, "", ""))
    template_runner._initialize_terraform()
    captured = capsys.readouterr()

    assert expected in captured.out


def test_check_matcha_directory_exists(
    capsys: SysCapture,
    template_runner: StateStorageTemplateRunner,
    matcha_testing_directory: str,
):
    """Test if service exit as expected and print out the expected error message when required files does not exists.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (StateStorageTemplateRunner): a StateStorageTemplateRunner object instance
        matcha_testing_directory (str): the test directory
    """
    os.chdir(matcha_testing_directory)

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


def test_apply_terraform(
    capsys: SysCapture, template_runner: StateStorageTemplateRunner
):
    """Test if terraform applied is handled correctly during apply when provisioning resources.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (StateStorageTemplateRunner): a StateStorageTemplateRunner object instance
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


def test_destroy_terraform(
    capsys: SysCapture, template_runner: StateStorageTemplateRunner
):
    """Test if terraform exception is captured when performing deprovision.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (StateStorageTemplateRunner): a StateStorageTemplateRunner object instance
    """
    template_runner.tfs.destroy = MagicMock(return_value=(0, "", ""))

    expected = "Destroying remote state management"

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


def test_provision(template_runner: StateStorageTemplateRunner):
    """Test service can provision resources using terraform.

    Args:
        template_runner (StateStorageTemplateRunner): a StateStorageTemplateRunner object instance
    """
    template_runner._check_terraform_installation = MagicMock()
    template_runner._validate_terraform_config = MagicMock()
    template_runner._initialize_terraform = MagicMock()
    template_runner._apply_terraform = MagicMock()
    template_runner._get_terraform_output = MagicMock()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        template_runner._initialize_terraform.assert_not_called()
        template_runner._apply_terraform.assert_not_called()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True
        template_runner.provision()
        template_runner._initialize_terraform.assert_called()
        template_runner._apply_terraform.assert_called()
        template_runner._get_terraform_output.assert_called()


def test_deprovision(template_runner: StateStorageTemplateRunner):
    """Test service can deprovision resources using terraform.

    Args:
        template_runner (StateStorageTemplateRunner): a StateStorageTemplateRunner object instance
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
