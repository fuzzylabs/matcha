"""Remote State Manager tests."""
import json
import os
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

from matcha_ml.errors import MatchaError
from matcha_ml.state import RemoteStateManager
from matcha_ml.state.remote_state_manager import (
    DEFAULT_CONFIG_NAME,
    RemoteStateBucketConfig,
    RemoteStateConfig,
)


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


@pytest.fixture
def remote_state_config() -> RemoteStateConfig:
    """Fixture for a remote state configuration.

    Returns:
        RemoteStateConfig: valid config
    """
    return RemoteStateConfig(
        remote_state_bucket=RemoteStateBucketConfig(
            account_name="test-account", container_name="test-container"
        )
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
    print(config_path)
    with open(config_path, "w") as f:
        f.write(remote_state_config.to_json())
    return matcha_testing_directory


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
