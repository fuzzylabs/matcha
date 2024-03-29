"""Test for the RemoteStateManager."""
import glob
import json
import os
from typing import Dict, Iterator
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from azure.mgmt.confluent.models._confluent_management_client_enums import (  # type: ignore [import]
    ProvisionState,
)

from matcha_ml.config import (
    DEFAULT_CONFIG_NAME,
    MatchaConfig,
    MatchaConfigService,
)
from matcha_ml.config.matcha_config import MatchaConfigComponent
from matcha_ml.errors import MatchaError
from matcha_ml.runners.remote_state_runner import RemoteStateRunner
from matcha_ml.state import RemoteStateManager
from matcha_ml.state.remote_state_manager import (
    ALREADY_LOCKED_MESSAGE,
    LOCK_FILE_NAME,
)
from matcha_ml.templates.remote_state_template import SUBMODULE_NAMES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)


@pytest.fixture
def broken_config_testing_directory(matcha_testing_directory: str) -> str:
    """Fixture for broken configuration file in temp working directory.

    Args:
        matcha_testing_directory (str): temporary working directory path

    Returns:
        str: temporary working directory path that the configuration was written to
    """
    config_path = os.path.join(matcha_testing_directory, DEFAULT_CONFIG_NAME)
    content = {}
    with open(config_path, "w") as f:
        json.dump(content, f)
    return matcha_testing_directory


@pytest.fixture
def valid_config_testing_directory(
    matcha_testing_directory: str, mocked_matcha_config: MatchaConfig
) -> str:
    """Fixture for a valid configuration file in temp working directory.

    Args:
        matcha_testing_directory (str): temporary working directory path
        mocked_matcha_config (RemoteStateConfig): configuration to write to the config file

    Returns:
        str: temporary working directory path that the configuration was written to
    """
    os.chdir(matcha_testing_directory)

    MatchaConfigService.write_matcha_config(mocked_matcha_config)

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


def test_provision_remote_state(
    matcha_testing_directory: str,
    mocked_matcha_config_json_object: Dict[str, Dict[str, str]],
    valid_config_testing_directory: str,
):
    """Test that provision_state_storage behaves as expected.

    We do not want to provision any resources in real environment.
    We will test whether the expected template for the infrastructure is created instead.

    Args:
        matcha_testing_directory (str): temporary working directory for tests.
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): the expected matcha config.
        valid_config_testing_directory (str): a testing directory containing a test config file.
    """
    os.chdir(matcha_testing_directory)

    remote_state_manager = RemoteStateManager(
        os.path.join(matcha_testing_directory, DEFAULT_CONFIG_NAME)
    )

    remote_state_manager.provision_remote_state("uksouth", "matcha")

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

    assert matcha_testing_directory == valid_config_testing_directory

    assert_matcha_config(matcha_testing_directory, mocked_matcha_config_json_object)


def test_deprovision_remote_state(matcha_testing_directory: str) -> None:
    """Test whether deprovision state storage behaves as expected.

    Args:
        matcha_testing_directory (str): temporary working directory for tests.
    """
    os.chdir(matcha_testing_directory)
    with patch(
        "matcha_ml.runners.remote_state_runner.RemoteStateRunner.deprovision"
    ) as destroy:
        destroy.return_value = None
        mock_config_path = os.path.join(matcha_testing_directory, DEFAULT_CONFIG_NAME)

        with open(mock_config_path, "a"):
            ...

        remote_state_manager = RemoteStateManager(config_path=mock_config_path)

        remote_state_manager.deprovision_remote_state()

        assert not os.path.exists(mock_config_path)

        template_runner = RemoteStateRunner()
        template_runner.deprovision.assert_called()


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
    with patch(
        "matcha_ml.state.remote_state_manager.AzureStorage.AzureClient.resource_group_state"
    ) as rg_state:
        rg_state.return_value = ProvisionState.SUCCEEDED
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


def test_lock_state(
    valid_config_testing_directory: str, mock_azure_storage_instance: MagicMock
):
    """Test remote state locking.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
        mock_azure_storage_instance (MagicMock): mock of AzureStorage instance
    """
    os.chdir(valid_config_testing_directory)
    remote_state = RemoteStateManager()
    remote_state.lock()
    mock_azure_storage_instance.create_empty.assert_called_with(
        container_name="test-container", blob_name=LOCK_FILE_NAME
    )


def test_state_already_locked(
    valid_config_testing_directory: str, mock_azure_storage_instance: MagicMock
):
    """Test remote state is already locked, hence failed to lock.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
        mock_azure_storage_instance (MagicMock): mock of AzureStorage instance
    """
    os.chdir(valid_config_testing_directory)
    mock_azure_storage_instance.create_empty.side_effect = MatchaError(
        ALREADY_LOCKED_MESSAGE
    )
    remote_state = RemoteStateManager()
    with pytest.raises(MatchaError):
        remote_state.lock()


def test_unlock_state(
    valid_config_testing_directory: str, mock_azure_storage_instance: MagicMock
):
    """Test remote state is unlocking.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
        mock_azure_storage_instance (MagicMock): mock of AzureStorage instance
    """
    os.chdir(valid_config_testing_directory)
    mock_azure_storage_instance.blob_exists.return_value = True

    remote_state = RemoteStateManager()
    remote_state.unlock()
    mock_azure_storage_instance.blob_exists.assert_called_with(
        container_name="test-container", blob_name=LOCK_FILE_NAME
    )
    mock_azure_storage_instance.delete_blob.assert_called_with(
        container_name="test-container", blob_name=LOCK_FILE_NAME
    )


def test_unlock_state_not_locked(
    valid_config_testing_directory: str, mock_azure_storage_instance: MagicMock
):
    """Test remote state is unlocking, which was not locked.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
        mock_azure_storage_instance (MagicMock): mock of AzureStorage instance
    """
    os.chdir(valid_config_testing_directory)
    mock_azure_storage_instance.blob_exists.return_value = False
    mock_azure_storage_instance.delete_blob.side_effect = Exception("Does not exist")

    remote_state = RemoteStateManager()
    remote_state.unlock()
    mock_azure_storage_instance.blob_exists.assert_called_with(
        container_name="test-container", blob_name=LOCK_FILE_NAME
    )
    mock_azure_storage_instance.delete_blob.assert_not_called()


def test_use_lock(
    valid_config_testing_directory: str, mock_azure_storage_instance: MagicMock
):
    """Test use_lock context manager.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
        mock_azure_storage_instance (MagicMock): mock of AzureStorage instance
    """
    os.chdir(valid_config_testing_directory)

    mock_azure_storage_instance.blob_exists.return_value = False

    remote_state = RemoteStateManager()
    with remote_state.use_lock():
        # Test that the state was locked
        mock_azure_storage_instance.create_empty.assert_called_with(
            container_name="test-container", blob_name=LOCK_FILE_NAME
        )
        assert mock_azure_storage_instance.create_empty.call_count == 1
        mock_azure_storage_instance.blob_exists.assert_not_called()
        mock_azure_storage_instance.delete_blob.assert_not_called()

        # Set azure storage mock into a locked state
        mock_azure_storage_instance.blob_exists.return_value = True

    # Test that the state was unlocked
    mock_azure_storage_instance.blob_exists.assert_called_with(
        container_name="test-container", blob_name=LOCK_FILE_NAME
    )
    mock_azure_storage_instance.delete_blob.assert_called_with(
        container_name="test-container", blob_name=LOCK_FILE_NAME
    )
    assert mock_azure_storage_instance.create_empty.call_count == 1
    assert mock_azure_storage_instance.blob_exists.call_count == 1
    assert mock_azure_storage_instance.delete_blob.call_count == 1


def test_use_lock_on_destroy_command(
    valid_config_testing_directory: str, mock_azure_storage_instance: MagicMock
):
    """Test use_lock context manager when destroy is True.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
        mock_azure_storage_instance (MagicMock): mock of AzureStorage instance
    """
    os.chdir(valid_config_testing_directory)

    mock_azure_storage_instance.blob_exists.return_value = False

    remote_state = RemoteStateManager()
    with remote_state.use_lock(destroy=True):
        # Test that the state was locked
        mock_azure_storage_instance.create_empty.assert_called_with(
            container_name="test-container", blob_name=LOCK_FILE_NAME
        )
        assert mock_azure_storage_instance.create_empty.call_count == 1
        mock_azure_storage_instance.blob_exists.assert_not_called()
        mock_azure_storage_instance.delete_blob.assert_not_called()

        # Set azure storage mock into a locked state
        mock_azure_storage_instance.blob_exists.return_value = True

    # Test that the state was not unlocked
    mock_azure_storage_instance.blob_exists.assert_not_called()
    mock_azure_storage_instance.delete_blob.assert_not_called()


def test_use_remote_state():
    """Test use_remote_state context manager."""
    remote_state_manager = RemoteStateManager()
    with patch.object(remote_state_manager, "upload") as mocked_upload, patch.object(
        remote_state_manager, "download"
    ) as mocked_download:
        with remote_state_manager.use_remote_state():
            mocked_download.assert_called_once_with(os.getcwd())
        mocked_upload.assert_called_once_with(os.path.join(".matcha", "infrastructure"))


def test_use_remote_state_on_destroy():
    """Test use_remote_state context manager and assert upload is not called when destroy is True."""
    remote_state_manager = RemoteStateManager()
    with patch.object(remote_state_manager, "upload") as mocked_upload, patch.object(
        remote_state_manager, "download"
    ) as mocked_download:
        with remote_state_manager.use_remote_state(destroy=True):
            mocked_download.assert_called_once_with(os.getcwd())
        mocked_upload.assert_not_called()


def test_is_state_provisioned_returns_false_when_resource_group_does_not_exist(
    valid_config_testing_directory: str, mock_azure_storage_instance: MagicMock
):
    """Test that is_state_provisioned returns False when the specified resource group does not exist.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
        mock_azure_storage_instance (MagicMock): mock of AzureStorage instance
    """
    os.chdir(valid_config_testing_directory)  # move to temporary working directory
    # Mock property resource_group_exists to return False (resource group does not exist)
    type(mock_azure_storage_instance).resource_group_exists = PropertyMock(
        return_value=False
    )

    remote_state = RemoteStateManager()

    assert not remote_state.is_state_provisioned()

    # Make sure the check for the storage container is not called
    mock_azure_storage_instance.container_exists.assert_not_called()


def test_is_state_stale_false(valid_config_testing_directory: str):
    """Test is_state_stale method returns False, when the user has a state file which has a resource group and container provisioned.

    Args:
        valid_config_testing_directory (str): temporary working directory path, with valid config file
    """
    os.chdir(valid_config_testing_directory)  # move to temporary working directory

    with patch(
        "matcha_ml.state.remote_state_manager.RemoteStateManager._configuration_file_exists"
    ) as config_file_exists, patch(
        "matcha_ml.state.remote_state_manager.RemoteStateManager._resource_group_exists"
    ) as resource_group_exists, patch(
        "matcha_ml.state.remote_state_manager.MatchaConfigService.read_matcha_config"
    ) as matcha_config:
        config_file_exists.return_value = True
        resource_group_exists.return_value = True
        matcha_config.return_value = MatchaConfig([])

        remote_state = RemoteStateManager()
        assert not remote_state.is_state_stale()


def test_is_state_stale_no_resource_group(matcha_testing_directory: str):
    """Test is_state_stale method returns True, when the specified resource group does not exist.

    Args:
        matcha_testing_directory (str): temporary working directory path
    """
    os.chdir(matcha_testing_directory)  # move to temporary working directory

    with patch(
        "matcha_ml.state.remote_state_manager.RemoteStateManager._configuration_file_exists"
    ) as config_file_exists, patch(
        "matcha_ml.state.remote_state_manager.RemoteStateManager._resource_group_exists"
    ) as resource_group_exists, patch(
        "matcha_ml.state.remote_state_manager.MatchaConfigService.read_matcha_config"
    ) as matcha_config, patch(
        "matcha_ml.state.remote_state_manager.MatchaConfig.find_component"
    ) as matcha_config_get_component:
        config_file_exists.return_value = True
        resource_group_exists.return_value = False
        matcha_config.return_value = MatchaConfig([])
        matcha_config_get_component.return_value = MatchaConfigComponent(
            name="remote_state_bucket", properties=[]
        )

        remote_state = RemoteStateManager()
        assert remote_state.is_state_stale()
