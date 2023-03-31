"""Tests for Terraform Service."""
import json
import os
from contextlib import nullcontext as does_not_raise
from unittest import mock
from unittest.mock import MagicMock

import pytest
import typer
from _pytest.capture import SysCapture
from python_terraform import TerraformCommandError

from matcha_ml.errors import MatchaTerraformError
from matcha_ml.templates.run_template import TerraformConfig, TerraformService


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


def test_is_approved_confirmed():
    """Test the user can accept a terraform action."""
    tfs = TerraformService()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True
        assert tfs.is_approved("do")


def test_is_approved_rejected():
    """Test the user can reject a terraform action."""
    tfs = TerraformService()

    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        assert not tfs.is_approved("do")


def test_check_installation_installed():
    """Test service can check if terraform is installed."""
    tfs = TerraformService()

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.return_value = (0, "", "")

        with does_not_raise():
            tfs.check_installation()


def test_check_installation_not_installed():
    """Test app exits when terraform is not installed."""
    tfs = TerraformService()

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.side_effect = TerraformCommandError(1, "", "", "")

        with pytest.raises(typer.Exit):
            tfs.check_installation()


def test_validate_config_not_exist(terraform_test_config: TerraformConfig):
    """Test application exits if there is no config.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config
    with pytest.raises(typer.Exit):
        tfs.validate_config()


def test_validate_config_exists(terraform_test_config: TerraformConfig):
    """Test service can validate that a config exists.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
    """
    infrastructure_directory = terraform_test_config.working_dir
    with open(
        os.path.join(infrastructure_directory, "terraform.tfvars.json"), "w"
    ) as f:
        f.write("{}")

    tfs = TerraformService()
    tfs.config = terraform_test_config
    with does_not_raise():
        tfs.validate_config()


def test_provision(terraform_test_config: TerraformConfig):
    """Test service can provision resources using terraform.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config
    tfs.check_installation = MagicMock()
    tfs.validate_config = MagicMock()
    tfs.terraform_client.init = MagicMock(return_value=(0, "", ""))
    tfs.terraform_client.apply = MagicMock(return_value=(0, "", ""))
    tfs.show_terraform_outputs = MagicMock()

    tfs.is_approved = MagicMock(
        return_value=False
    )  # the user does not approve, should not provision
    with pytest.raises(typer.Exit):
        tfs.provision()
        tfs.terraform_client.init.assert_not_called()
        tfs.terraform_client.apply.assert_not_called()
        tfs.show_terraform_outputs.assert_not_called()

    tfs.is_approved = MagicMock(
        return_value=True
    )  # the user approves, should provision
    with does_not_raise():
        tfs.provision()
        tfs.terraform_client.init.assert_called()
        tfs.terraform_client.apply.assert_called()
        tfs.show_terraform_outputs.assert_called()


def test_deprovision(terraform_test_config: TerraformConfig):
    """Test service can destroy resources using terraform.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config
    tfs.check_installation = MagicMock()
    tfs.terraform_client.destroy = MagicMock(return_value=(0, "", ""))

    tfs.is_approved = MagicMock(
        return_value=False
    )  # the user does not approve, should not provision
    with pytest.raises(typer.Exit):
        tfs.deprovision()
        tfs.terraform_client.destroy.assert_not_called()

    tfs.is_approved = MagicMock(
        return_value=True
    )  # the user approves, should provision
    with does_not_raise():
        tfs.deprovision()
        tfs.terraform_client.destroy.assert_called()


def test_write_outputs_state(terraform_test_config: TerraformConfig):
    """Test service writes the state file correctly.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config

    def mock_output(name: str, full_value: bool):
        if name == "mlflow-tracking-url" and full_value:
            return "mlflow-test-url"
        else:
            raise ValueError("Unexpected input")

    tfs.terraform_client.output = MagicMock(wraps=mock_output)

    with does_not_raise():
        expected_output = {"mlflow-tracking-url": "mlflow-test-url"}
        tfs.write_outputs_state()
        with open(terraform_test_config.state_file) as f:
            assert json.load(f) == expected_output


def test_show_terraform_outputs(
    terraform_test_config: TerraformConfig, capsys: SysCapture
):
    """Test service shows the correct terraform output.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config

    def mock_output(name: str, full_value: bool):
        if name == "mlflow-tracking-url" and full_value:
            return "mlflow-test-url"
        else:
            raise ValueError("Unexpected input")

    tfs.terraform_client.output = MagicMock(wraps=mock_output)
    with does_not_raise():
        tfs.show_terraform_outputs()
        captured = capsys.readouterr()
        assert '"mlflow-tracking-url": "mlflow-test-url"' in captured.out


def test_terraform_raise_exception_provision_init(
    terraform_test_config: TerraformConfig,
):
    """Test if terraform exception is handled correctly during init when provisioning resources.

    Args:
        terraform_test_config (TerraformConfig): terraform test service config
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config
    tfs.check_installation = MagicMock()
    tfs.validate_config = MagicMock()
    tfs.terraform_client.init = MagicMock(return_value=(1, "", ""))

    tfs.is_approved = MagicMock(
        return_value=True
    )  # the user approves, should provision

    with pytest.raises(MatchaTerraformError):
        tfs.provision()
        tfs.terraform_client.init.assert_not_called()


def test_terraform_raise_exception_provision_apply(
    terraform_test_config: TerraformConfig,
):
    """Test if terraform exception is handled correctly during apply when provisioning resources.

    Args:
        terraform_test_config (TerraformConfig): terraform test service config
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config
    tfs.check_installation = MagicMock()
    tfs.validate_config = MagicMock()
    tfs.terraform_client.init = MagicMock(return_value=(0, "", ""))
    tfs.terraform_client.apply = MagicMock(return_value=(1, "", ""))
    tfs.show_terraform_outputs = MagicMock()

    tfs.is_approved = MagicMock(
        return_value=True
    )  # the user approves, should provision

    with pytest.raises(MatchaTerraformError):
        tfs.provision()
        tfs.terraform_client.init.assert_called()
        tfs.terraform_client.apply.assert_not_called()
        tfs.show_terraform_outputs.assert_not_called()


def test_terraform_raise_exception_deprovision_destroy(
    terraform_test_config: TerraformConfig,
):
    """Test if terraform exception is captured when performing deprovision.

    Args:
        terraform_test_config (TerraformConfig): terraform test service config
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config

    tfs.check_installation = MagicMock()
    tfs.terraform_client.destroy = MagicMock(return_value=(1, "", ""))

    tfs.is_approved = MagicMock(
        return_value=True
    )  # the user approves, should deprovision

    with pytest.raises(MatchaTerraformError):
        tfs.deprovision()
        tfs.terraform_client.destroy.assert_called()
