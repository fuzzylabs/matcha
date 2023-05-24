"""Test for the RemoteStateManager."""
import glob
import json
import os
import shutil
from typing import Dict, Iterator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import SysCapture

from matcha_ml.errors import MatchaError
from matcha_ml.state.remote_state_manager import (
    DEFAULT_CONFIG_NAME,
    RemoteStateBucketConfig,
    RemoteStateConfig,
    RemoteStateManager,
)
from matcha_ml.templates.build_templates.state_storage_template import SUBMODULE_NAMES
from matcha_ml.templates.run_state_storage_template import TemplateRunner

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)


@pytest.fixture
def remote_state_config() -> RemoteStateConfig:
    """Fixture for a remote state configuration.

    Returns:
        RemoteStateConfig: valid config
    """
    return RemoteStateConfig(
        remote_state_bucket=RemoteStateBucketConfig(
            account_name="test-account",
            container_name="test-container",
            resource_group_name="test-rg",
        )
    )


@pytest.fixture
def expected_matcha_config() -> Dict[str, Dict[str, str]]:
    """A fixture for the expected json configuration for testing whether configs are generated as expected.

    Returns:
        Dict[str, Dict[str, str]]: the expected matcha configuration.
    """
    config = {
        "remote_state_bucket": {
            "account_name": "test-account",
            "container_name": "test-container",
            "resource_group_name": "test-rg",
        }
    }
    return config


@pytest.fixture
def broken_config_testing_directory(matcha_testing_directory: str) -> str:
    """Fixture for broken configuration file in temp working directory.

    Args:
        matcha_testing_directory (str): temporary working directory path

    Returns:
        str: temporary working directory path that the configuration was written to
    """
    config_path = os.path.join(matcha_testing_directory, DEFAULT_CONFIG_NAME)
    print(config_path)
    content = {}
    with open(config_path, "w") as f:
        json.dump(content, f)
    return matcha_testing_directory


@pytest.fixture
def valid_config_testing_directory(
    matcha_testing_directory: str, remote_state_config: RemoteStateConfig
) -> str:
    """Fixture for a valid configuration file in temp working directory.

    Args:
        matcha_testing_directory (str): temporary working directory path
        remote_state_config (RemoteStateConfig): configuration to write to the config file

    Returns:
        str: temporary working directory path that the configuration was written to
    """
    config_path = os.path.join(matcha_testing_directory, DEFAULT_CONFIG_NAME)

    with open(config_path, "w") as f:
        f.write(remote_state_config.to_json())

    return matcha_testing_directory


@pytest.fixture
def mock_azure_storage_instance() -> Iterator[MagicMock]:
    """Mock Azure Storage instance.

    Yields:
        MagicMock: of Azure Storage instance
    """
    class_stub = "matcha_ml.state.remote_state_manager.AzureStorage"
    with patch(class_stub) as mock_azure_storage:
        mock_azure_storage_instance = mock_azure_storage.return_value
        yield mock_azure_storage_instance


def assert_infrastructure(
    destination_path: str,
    expected_tf_vars: Dict[str, str],
):
    """Assert if the infrastructure configuration is valid.

    Args:
        destination_path (str): infrastructure config destination path
        expected_tf_vars (Dict[str, str]): expected Terraform variables
    """
    # Test that destination path is a directory
    assert os.path.exists(destination_path)

    for module_file_name in glob.glob(os.path.join(TEMPLATE_DIR, "*.tf")):
        module_file_path = os.path.join(destination_path, module_file_name)
        assert os.path.exists(module_file_path)

    for module_name in SUBMODULE_NAMES:
        for module_file_name in glob.glob(
            os.path.join(TEMPLATE_DIR, module_name, "*.tf")
        ):
            module_file_path = os.path.join(
                destination_path, module_name, module_file_name
            )
            assert os.path.exists(module_file_path)

    # Check that Terraform variables file exists and content is equal/correct
    variables_file_path = os.path.join(destination_path, "terraform.tfvars.json")
    assert os.path.exists(variables_file_path)

    with open(variables_file_path) as f:
        tf_vars = json.load(f)

    assert tf_vars == expected_tf_vars


def assert_matcha_config(
    project_root_path: str,
    expected_config: Dict[str, Dict[str, str]],
):
    """Assert if the matcha configuration is valid.

    Args:
        project_root_path (str): the root of the project, where the matcha configuration should live
        expected_config (Dict[str, Dict[str, str]]): expected matcha configurations
    """
    # Check that Terraform variables file exists and content is equal/correct
    matcha_config_file_path = os.path.join(project_root_path, DEFAULT_CONFIG_NAME)
    assert os.path.exists(matcha_config_file_path)

    with open(matcha_config_file_path) as f:
        matcha_config = json.load(f)

    assert matcha_config == expected_config


def test_provision_state_storage(
    matcha_testing_directory: str, expected_matcha_config: Dict[str, Dict[str, str]]
):
    """Test that provision_state_storage behaves as expected.

    We do not want to provision any resources in real environment.
    We will test whether the expected template for the infrastructure is created instead.

    Args:
        matcha_testing_directory (str): temporary working directory for tests.
        expected_matcha_config (Dict[str, Dict[str, str]]): the expected matcha config.
    """
    os.chdir(matcha_testing_directory)

    remote_state_manager = RemoteStateManager(
        os.path.join(matcha_testing_directory, DEFAULT_CONFIG_NAME)
    )

    remote_state_manager.provision_state_storage("uksouth", "matcha")

    state_storage_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "remote_state_storage"
    )

    state_storage_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
    }

    assert_infrastructure(
        state_storage_destination_path, state_storage_expected_tf_vars
    )

    assert_matcha_config(matcha_testing_directory, expected_matcha_config)


def test_deprovision_state_storage(capsys: SysCapture) -> None:
    """Test whether deprovision state storage behaves as expected.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    with patch(
        "matcha_ml.templates.run_state_storage_template.TemplateRunner.deprovision"
    ) as destroy:
        destroy.return_value = None
        remote_state_manager = RemoteStateManager()

        remote_state_manager.deprovision_state_storage()

        captured = capsys.readouterr()

        expected_output = "Destroying remote state management is complete!"

        template_runner = TemplateRunner()
        template_runner.deprovision.assert_called()

        assert expected_output in captured.out


def test_write_matcha_config(
    matcha_testing_directory: str, expected_matcha_config: Dict[str, Dict[str, str]]
):
    """Test whether the write_matcha_config() function is able to write the expected config to the expected destination.

    Args:
        matcha_testing_directory (str): temporary working directory for tests.
        expected_matcha_config (Dict[str, Dict[str, str]]): the expected matcha config.
    """
    os.chdir(matcha_testing_directory)
    remote_state_manager = RemoteStateManager(
        os.path.join(matcha_testing_directory, DEFAULT_CONFIG_NAME)
    )

    remote_state_manager._write_matcha_config(
        "test-account", "test-container", "test-rg"
    )

    assert_matcha_config(matcha_testing_directory, expected_matcha_config)


def test_is_state_provisioned_true(
    valid_config_testing_directory: str, mock_azure_storage_instance: MagicMock
):
    """Test is_state_provisioned method, when everything is provisioned.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
        mock_azure_storage_instance (MagicMock): mock of AzureStorage instance
    """
    os.chdir(valid_config_testing_directory)  # move to temporary working directory
    mock_azure_storage_instance.container_exists.return_value = True
    remote_state = RemoteStateManager()
    assert remote_state.is_state_provisioned()


def test_is_state_provisioned_no_config(matcha_testing_directory: str):
    """Test is_state_provisioned method returns False, when no config file is present.

    Args:
        matcha_testing_directory (str): temporary working directory path
    """
    os.chdir(matcha_testing_directory)  # move to temporary working directory
    remote_state = RemoteStateManager()
    assert not remote_state.is_state_provisioned()


def test_is_state_provisioned_broken_config(broken_config_testing_directory: str):
    """Test is_state_provisioned method returns False, when the configuration file is broken.

    Args:
        broken_config_testing_directory (str): temporary working directory path, with broken config file
    """
    os.chdir(broken_config_testing_directory)  # move to temporary working directory
    remote_state = RemoteStateManager()
    with pytest.raises(MatchaError):
        assert not remote_state.is_state_provisioned()


def test_is_state_provisioned_broken_no_bucket(
    valid_config_testing_directory: str, mock_azure_storage_instance: MagicMock
):
    """Test is_state_provisioned method returns False, when Azure Storage container is not provisioned.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
        mock_azure_storage_instance (MagicMock): mock of AzureStorage instance
    """
    os.chdir(valid_config_testing_directory)  # move to temporary working directory
    mock_azure_storage_instance.container_exists.return_value = False
    remote_state = RemoteStateManager()
    assert not remote_state.is_state_provisioned()


def test_use_remote_state(matcha_testing_directory: str):
    """Test use_remote_state context manager executes functionality between downlaod and upload.

    Args:
        matcha_testing_directory (str): temporary working directory path
    """
    mocked_azure_blob_path = os.path.join(matcha_testing_directory, "blob")
    mocked_local_storage_path = os.path.join(matcha_testing_directory, "local")
    mocked_azure_blob_file = os.path.join(mocked_azure_blob_path, "test", "test.txt")
    mocked_local_storage_file = os.path.join(
        mocked_local_storage_path, "test", "test.txt"
    )
    os.mkdir(mocked_azure_blob_path)
    os.mkdir(mocked_local_storage_path)

    def mocked_upload(*args) -> None:
        """Mocked upload function for the use_remote_state context manager.

        Args:
            *args (str): placeholder for the upload function positional arguments
        """
        shutil.copytree(
            mocked_local_storage_path, mocked_azure_blob_path, dirs_exist_ok=True
        )

    def mocked_download(*args) -> None:
        """Mocked download function for the use_remote_state context manager.

        Args:
            *args (str): placeholder for the download function positional arguments
        """
        shutil.copytree(
            mocked_azure_blob_path, mocked_local_storage_path, dirs_exist_ok=True
        )

    with patch.object(
        RemoteStateManager, "download", new=mocked_download
    ), patch.object(RemoteStateManager, "upload", new=mocked_upload):
        remote_state_manager = RemoteStateManager()
        # test create locally and upload
        assert not os.path.isfile(mocked_azure_blob_file)
        with remote_state_manager.use_remote_state():
            os.mkdir(os.path.join(mocked_local_storage_path, "test"))
            with open(os.path.join(mocked_local_storage_file), "w") as file:
                file.write("Hello, world!")
        assert os.path.isfile(os.path.join(mocked_local_storage_file))
        assert os.path.isfile(mocked_azure_blob_file)
        # test download from blob
        shutil.rmtree(mocked_local_storage_path)
        assert not os.path.isfile(os.path.join(mocked_local_storage_file))
        with remote_state_manager.use_remote_state():
            pass
        assert os.path.isfile(os.path.join(mocked_local_storage_file))
        # test overwrite blob
        with open(mocked_azure_blob_file) as file:
            assert file.read() == "Hello, world!"
        with remote_state_manager.use_remote_state(), open(
            os.path.join(mocked_local_storage_file), "w"
        ) as file:
            file.write("Hello, Matcha!")
        with open(mocked_azure_blob_file) as file:
            assert file.read() == "Hello, Matcha!"
        # test delete from blob
        # assert os.path.isfile(mocked_azure_blob_file)
        # with remote_state_manager.use_remote_state():
        #     shutil.rmtree(os.path.join(mocked_local_storage_path, "test"))
        # assert not os.path.isfile(mocked_azure_blob_file)
        # assert False
