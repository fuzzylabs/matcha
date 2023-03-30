"""Tests for Terraform Service."""
import json
import os
from contextlib import nullcontext as does_not_raise
from distutils.dir_util import copy_tree
from unittest import mock
from unittest.mock import MagicMock

import pytest
import typer
from _pytest.capture import SysCapture
from python_terraform import TerraformCommandError

from matcha_ml.errors import MatchaTerraformError
from matcha_ml.templates.build_templates.azure_template import (
    TemplateVariables,
    build_template,
)
from matcha_ml.templates.run_template import TerraformConfig, TerraformService

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)


@pytest.fixture
def template_src_path() -> str:
    """Fixture for the test infrastructure template path.

    Returns:
        str: template path
    """
    return TEMPLATE_DIR


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
        var_file=os.path.join(infrastructure_directory, "terraform.tfvars.json")
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


def test_terraform_exception_provision_when_missing_config(
    terraform_test_config: TerraformConfig, template_src_path: str
):
    """Test if terraform exception is handled correctly during apply when the main.tf file does not exist.

    Args:
        terraform_test_config (TerraformConfig): terraform test service config
        template_src_path (str): existing template directory path
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config

    # copy tf files to run provision
    src_path = template_src_path
    dest_path = terraform_test_config.working_dir
    copy_tree(src_path, dest_path)
    config = TemplateVariables("uksouth", "matcha")
    build_template(config, template_src_path, dest_path)

    # delete a file to simulate exception
    os.remove(os.path.join(dest_path, "resource_group/main.tf"))

    tfs.is_approved = MagicMock(
        return_value=True
    )  # the user approves, should provision

    with pytest.raises(MatchaTerraformError):
        tfs.provision()
        tfs.terraform_client.init.assert_called()
        tfs.terraform_client.apply.assert_called()
        tfs.show_terraform_outputs.assert_not_called()


def test_terraform_deprovision_config_does_not_exist_exception(
    terraform_test_config: TerraformConfig, template_src_path: str
):
    """Test if terraform exception is captured when performing deprovision on a config that does not exist.

    Args:
        terraform_test_config (TerraformConfig): terraform test service config
        template_src_path (str): existing template directory path
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config

    # copy tf files to run provision
    src_path = template_src_path
    dest_path = terraform_test_config.working_dir
    copy_tree(src_path, dest_path)

    # Create a config with a resource group name that does not exist
    config = TemplateVariables("uksouth", "KGFUSQXGNZKJPMUAIIAZ")
    build_template(config, template_src_path, dest_path)

    tfs.is_approved = MagicMock(
        return_value=True
    )  # the user approves, should provision

    with pytest.raises(MatchaTerraformError):
        tfs.deprovision()
