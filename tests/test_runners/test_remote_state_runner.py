"""Test for interacting with terraform service to run the state storage template."""
import os
from typing import Callable, Dict, Union
from unittest import mock
from unittest.mock import MagicMock

import pytest

from matcha_ml.runners import RemoteStateRunner
from matcha_ml.services.terraform_service import TerraformConfig


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
def template_runner() -> RemoteStateRunner:
    """Return a template runner object instance for test.

    Returns:
        RemoteStateRunner: a RemoteStateRunner object instance.
    """
    return RemoteStateRunner()


def test_provision(template_runner: RemoteStateRunner):
    """Test service can provision resources using terraform.

    Args:
        template_runner (RemoteStateRunner): a RemoteStateRunner object instance
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


def test_deprovision(template_runner: RemoteStateRunner):
    """Test service can deprovision resources using terraform.

    Args:
        template_runner (RemoteStateRunner): a RemoteStateRunner object instance
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
