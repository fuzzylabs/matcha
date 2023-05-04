"""Tests for Terraform Service."""
import os
from unittest import mock
from unittest.mock import MagicMock

import pytest
from python_terraform import TerraformCommandError

from matcha_ml.services.terraform_service import TerraformConfig, TerraformService


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


def test_check_installation_installed():
    """Test service can check if terraform is installed."""
    tfs = TerraformService()

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.return_value = (0, "", "")

        assert tfs.check_installation()


def test_check_installation_not_installed():
    """Test service can check if terraform is not installed."""
    tfs = TerraformService()

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.side_effect = TerraformCommandError(1, "", "", "")

        assert not tfs.check_installation()


def test_check_matcha_directory_exists(tmp_path: str):
    """Test service can check if .matcha file exists within current working directory and if it's empty.

    Args:
        tmp_path (str): Pytest temporary path fixture for testing.
    """
    # Create a new directory within the temporary directory
    new_dir = tmp_path / ".matcha"
    os.mkdir(new_dir)
    os.chdir(tmp_path)

    # Create an infrastructure directory in the new directory
    dir_name = "infrastructure"
    os.path.join(new_dir, dir_name)
    os.mkdir(os.path.join(new_dir, dir_name))

    tfs = TerraformService()

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.return_value = (0, "", "")

        assert tfs.check_matcha_directory_exists()

        assert tfs.check_matcha_directory_integrity()

    os.chdir("..")


def test_check_matcha_directory_does_not_exist():
    """Test service returns False if .matcha file does not exists within current working directory.

    Args:
        tmp_path (str): Pytest temporary path fixture for testing.
    """
    tfs = TerraformService()

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.side_effect = TerraformCommandError(1, "", "", "")

        assert not tfs.check_matcha_directory_exists()


def test_check_matcha_directory_integrity(tmp_path):
    """Test service returns False when .matcha file is empty.

    Args:
        tmp_path (str): Pytest temporary path fixture for testing.
    """
    # Create a new directory within the temporary directory
    new_dir = tmp_path / ".matcha"
    os.mkdir(new_dir)
    os.chdir(tmp_path)

    tfs = TerraformService()

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.return_value = (0, "", "")

        assert not tfs.check_matcha_directory_integrity()

    os.chdir("..")


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
    assert tfs.validate_config()


def test_validate_config_not_exist(terraform_test_config: TerraformConfig):
    """Test service return False if there is no config.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
    """
    tfs = TerraformService()
    tfs.config = terraform_test_config
    assert not tfs.validate_config()


def test_get_tf_state_dir(tmp_path):
    """Test get_previous_temp_dir returns the .temp directory.

    Args:
        tmp_path (str): Pytest temporary path fixture for testing.
    """
    new_dir = tmp_path / "terraform.tfstate"
    os.mkdir(new_dir)

    tfs = TerraformService()

    path = tfs.get_tf_state_dir()

    # Extract the last component of the path otherwise it will return full path
    last_component = os.path.basename(path)

    assert last_component == "terraform.tfstate"


def test_init():
    """Test if service init() calls terraform_client.init()."""
    tfs = TerraformService()

    tfs.terraform_client.init = MagicMock(return_value=(0, "", ""))

    _, _, _ = tfs.init()

    tfs.terraform_client.init.assert_called()


def test_apply():
    """Test if service apply() calls terraform_client.apply()."""
    tfs = TerraformService()

    tfs.terraform_client.apply = MagicMock(return_value=(0, "", ""))

    _, _, _ = tfs.apply()

    tfs.terraform_client.apply.assert_called()


def test_destroy():
    """Test if service destroy() calls terraform_client.destroy()."""
    tfs = TerraformService()

    tfs.terraform_client.destroy = MagicMock(return_value=(0, "", ""))

    _, _, _ = tfs.destroy()

    tfs.terraform_client.destroy.assert_called()
