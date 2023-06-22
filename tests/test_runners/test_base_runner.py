"""Test for testing BaseRuner class."""
import os
from unittest import mock
from unittest.mock import MagicMock

import pytest
import typer
from _pytest.capture import SysCapture

from matcha_ml.errors import MatchaTerraformError
from matcha_ml.runners.base_runner import BaseRunner

CLASS_STUB = "matcha_ml.runners.base_runner.BaseRunner"


def test_check_terraform_installation(capsys: SysCapture):
    """Test app exits when terraform is not installed.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    expected = "Terraform is not installed"
    runner = BaseRunner()
    runner.tfs = MagicMock()
    runner.tfs.check_installation.return_value = False
    with pytest.raises(typer.Exit):
        runner._check_terraform_installation()
    captured = capsys.readouterr()

    assert expected in captured.err


def test_validate_terraform_config(capsys: SysCapture):
    """Test application exits if there is no config.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    expected = "The file terraform.tfvars.json was not found"

    runner = BaseRunner()
    runner.tfs = MagicMock()
    runner.tfs.validate_config.return_value = False

    with pytest.raises(typer.Exit):
        runner._validate_terraform_config()
    captured = capsys.readouterr()

    assert expected in captured.err


def test_check_matcha_directory_exists(
    capsys: SysCapture,
    matcha_testing_directory: str,
):
    """Test if service exit as expected and print out the expected error message when required files does not exists.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        matcha_testing_directory (str): the test directory
    """
    os.chdir(matcha_testing_directory)

    template_runner = BaseRunner()
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


def test_initialize_terraform(capsys: SysCapture):
    """Test if service behaves as expected when initializing Terraform.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    template_runner = BaseRunner()
    template_runner.tf_state_dir = MagicMock()

    with mock.patch.object(template_runner.tf_state_dir, "exists", return_value=True):
        expected = "has already been initialized"

        template_runner._initialize_terraform()

        captured = capsys.readouterr()

        assert expected in captured.out

    with mock.patch.object(template_runner.tf_state_dir, "exists", return_value=False):
        template_runner.tfs.init = MagicMock(return_value=(0, "", ""))
        expected = " initialized!"
        template_runner._initialize_terraform()

        captured = capsys.readouterr()

        assert expected in captured.out


def test_apply_terraform(capsys: SysCapture):
    """Test if terraform applied is handled correctly during apply when provisioning resources.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    template_runner = BaseRunner()
    template_runner.tfs.apply = MagicMock(return_value=(0, "", ""))
    expected = "Resources for matcha to work have been provisioned!"

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


def test_destroy_terraform(capsys: SysCapture):
    """Test if terraform exception is captured when performing deprovision.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
        template_runner (AzureTemplateRunner): a AzureTemplateRunner object instance
    """
    template_runner = BaseRunner()
    template_runner.tfs.destroy = MagicMock(return_value=(0, "", ""))

    expected = "Destroying your resources"

    template_runner._destroy_terraform(msg="your")

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


def test_provision():
    """Test provision function in BaseRunner class raises NotImplemented exception."""
    template_runner = BaseRunner()
    with pytest.raises(NotImplementedError):
        template_runner.provision()


def test_deprovision():
    """Test deprovision function in BaseRunner class raises NotImplemented exception."""
    template_runner = BaseRunner()
    with pytest.raises(NotImplementedError):
        template_runner.deprovision()
