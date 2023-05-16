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
    return TerraformConfig(working_dir=infrastructure_directory)


def test_check_installation_installed(terraform_test_config: TerraformConfig):
    """Test service can check if terraform is installed.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
    """
    tfs = TerraformService(terraform_test_config)

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.return_value = (0, "", "")

        assert tfs.check_installation()


def test_check_installation_not_installed(terraform_test_config: TerraformConfig):
    """Test service can check if terraform is not installed.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
    """
    tfs = TerraformService(terraform_test_config)

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.side_effect = TerraformCommandError(1, "", "", "")

        assert not tfs.check_installation()


def test_check_matcha_directory_exists(
    tmp_path: str, terraform_test_config: TerraformConfig
):
    """Test service can check if .matcha file exists within current working directory and if it's empty.

    Args:
        tmp_path (str): Pytest temporary path fixture for testing.
        terraform_test_config (TerraformConfig): test terraform service config.
    """
    # Create a new directory within the temporary directory
    new_dir = tmp_path / ".matcha"
    os.mkdir(new_dir)
    os.chdir(tmp_path)

    # Create an infrastructure directory in the new directory
    dir_name = "infrastructure"
    os.path.join(new_dir, dir_name)
    os.mkdir(os.path.join(new_dir, dir_name))

    tfs = TerraformService(terraform_test_config)

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.return_value = (0, "", "")

        assert tfs.check_matcha_directory_exists()

        assert tfs.check_matcha_directory_integrity()

    os.chdir("..")


def test_check_matcha_directory_does_not_exist(terraform_test_config: TerraformConfig):
    """Test service returns False if .matcha file does not exists within current working directory.

    Args:
        tmp_path (str): Pytest temporary path fixture for testing.
        terraform_test_config (TerraformConfig): test terraform service config.
    """
    tfs = TerraformService(terraform_test_config)

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.side_effect = TerraformCommandError(1, "", "", "")

        assert not tfs.check_matcha_directory_exists()


def test_check_matcha_directory_integrity(
    tmp_path, terraform_test_config: TerraformConfig
):
    """Test service returns False when .matcha file is empty.

    Args:
        tmp_path (str): Pytest temporary path fixture for testing.
        terraform_test_config (TerraformConfig): test terraform service config.
    """
    # Create a new directory within the temporary directory
    new_dir = tmp_path / ".matcha"
    os.mkdir(new_dir)
    os.chdir(tmp_path)

    tfs = TerraformService(terraform_test_config)

    with mock.patch("python_terraform.Terraform") as mock_tf:
        mock_tf_instance = mock_tf.return_value
        mock_tf_instance.cmd.return_value = (0, "", "")

        assert not tfs.check_matcha_directory_integrity()

    os.chdir("..")


def test_verify_kubectl_config_file(
    tmpdir: str, terraform_test_config: TerraformConfig
):
    """Test whether kubeconfig is present as path ~/.kube/config.

    Args:
        tmpdir (str): Temporary directory
        terraform_test_config (TerraformConfig): test terraform service config.
    """
    temp_path = tmpdir.mkdir(".kube").join("config")
    tmp_config_file_path = os.path.join(os.path.expanduser("~"), temp_path)

    # Check if path to config file does not exists
    assert not os.path.exists(tmp_config_file_path)

    # Check if config file is not present
    assert not os.path.isfile(tmp_config_file_path)

    tfs = TerraformService(terraform_test_config)

    tfs.verify_kubectl_config_file(tmp_config_file_path)

    # Check if path to config file exists
    assert os.path.exists(tmp_config_file_path)

    # Check if config file is created
    assert os.path.isfile(tmp_config_file_path)


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

    tfs = TerraformService(terraform_test_config)
    assert tfs.validate_config()


def test_validate_config_not_exist(terraform_test_config: TerraformConfig):
    """Test service return False if there is no config.

    Args:
        terraform_test_config (TerraformConfig): test terraform service config
    """
    tfs = TerraformService(terraform_test_config)
    assert not tfs.validate_config()


def test_get_tf_state_dir(tmp_path, terraform_test_config: TerraformConfig):
    """Test get_previous_temp_dir returns the path of the terraform.tfstate file.

    Args:
        tmp_path (str): Pytest temporary path fixture for testing.
        terraform_test_config (TerraformConfig): test terraform service config.
    """
    new_dir = tmp_path / "terraform.tfstate"
    os.mkdir(new_dir)

    tfs = TerraformService(terraform_test_config)

    path = tfs.get_tf_state_dir()

    # Extract the last component of the path otherwise it will return full path
    last_component = os.path.basename(path)

    assert last_component == "terraform.tfstate"


def test_init(terraform_test_config: TerraformConfig):
    """Test if service init() calls terraform_client.init().

    Args:
        terraform_test_config (TerraformConfig): test terraform service config.
    """
    tfs = TerraformService(terraform_test_config)

    tfs.terraform_client.init = MagicMock(return_value=(0, "", ""))

    _, _, _ = tfs.init()

    tfs.terraform_client.init.assert_called()


def test_apply(terraform_test_config: TerraformConfig):
    """Test if service apply() calls terraform_client.apply().

    Args:
        terraform_test_config (TerraformConfig): test terraform service config.
    """
    tfs = TerraformService(terraform_test_config)

    tfs.terraform_client.apply = MagicMock(return_value=(0, "", ""))

    _, _, _ = tfs.apply()

    tfs.terraform_client.apply.assert_called()


def test_destroy(terraform_test_config: TerraformConfig):
    """Test if service destroy() calls terraform_client.destroy().

    Args:
        terraform_test_config (TerraformConfig): test terraform service config.
    """
    tfs = TerraformService(terraform_test_config)

    tfs.terraform_client.destroy = MagicMock(return_value=(0, "", ""))

    _, _, _ = tfs.destroy()

    tfs.terraform_client.destroy.assert_called()
