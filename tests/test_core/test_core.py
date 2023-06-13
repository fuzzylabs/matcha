"""Test suite to test the core matcha commands and all its subcommands."""
import json
import os
from typing import Dict, Iterable, Iterator, Union
from unittest import mock
from unittest.mock import MagicMock

import pytest
import yaml

from matcha_ml.cli.cli import app
from matcha_ml.core.core import get, remove_state_lock
from matcha_ml.errors import MatchaInputError
from matcha_ml.services.global_parameters_service import GlobalParameters

INTERNAL_FUNCTION_STUB = "matcha_ml.services.global_parameters_service.GlobalParameters"


@pytest.fixture(autouse=True)
def mock_state_file(matcha_testing_directory: str):
    """A fixture for mocking a test state file in the test directory.

    Args:
        matcha_testing_directory (str): the test directory
    """
    os.chdir(matcha_testing_directory)

    matcha_infrastructure_dir = os.path.join(".matcha", "infrastructure", "resources")
    os.makedirs(matcha_infrastructure_dir)
    matcha_state_path = os.path.join(".matcha", "infrastructure", "matcha.state")

    state_file_resources = {
        "cloud": {"flavor": "azure", "resource-group-name": "test_resources"},
        "container-registry": {
            "flavor": "azure",
            "registry-name": "azure_registry_name",
            "registry-url": "azure_container_registry",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
    }

    with open(matcha_state_path, "w") as f:
        json.dump(state_file_resources, f)


@pytest.fixture
def expected_outputs() -> dict:
    """The expected state file initialized.

    Returns:
        dict: expected output
    """
    outputs = {
        "cloud": {"flavor": "azure", "resource-group-name": "test_resources"},
        "container-registry": {
            "flavor": "azure",
            "registry-name": "azure_registry_name",
            "registry-url": "azure_container_registry",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
    }

    return outputs


@pytest.fixture(autouse=True)
def teardown_singleton():
    """Tears down the singleton before each test case by clearing the current object."""
    GlobalParameters._instance = None


@pytest.fixture(autouse=True)
def mock_provisioned_remote_state() -> Iterable[MagicMock]:
    """Mock remote state manager to have state provisioned.

    Returns:
        MagicMock: mock of an RemoteStateManager instance
    """
    with mock.patch(
        "matcha_ml.core.core.RemoteStateManager"
    ) as mock_state_manager_class:
        mock_state_manager = mock_state_manager_class.return_value
        mock_state_manager.is_state_provisioned.return_value = True
        mock_state_manager.get_hash_remote_state.return_value = (
            "470544910b3fe623e00d63e6314588a3"
        )
        yield mock_state_manager


@pytest.fixture
def mock_azure_storage_instance() -> Iterator[MagicMock]:
    """Mock Azure Storage instance.

    Yields:
        MagicMock: of Azure Storage instance
    """
    class_stub = "matcha_ml.state.remote_state_manager.AzureStorage"
    with mock.patch(class_stub) as mock_azure_storage:
        mock_azure_storage_instance = mock_azure_storage.return_value
        yield mock_azure_storage_instance


@pytest.fixture
def expected_configuration() -> Dict[str, Union[str, bool]]:
    """Pytest fixture to return expected configuration.

    Returns:
        Dict[str, Union[str, bool]]: Dictionary containing expected configuration
    """
    return {"analytics_opt_out": False, "user_id": "dummy_user_id"}


def test_get_resources(
    mock_provisioned_remote_state: MagicMock, expected_outputs: dict
):
    """Test get resources function with no resource specified.

    Args:
        mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
        expected_outputs (dict): The expected output from the matcha state file.
    """
    assert expected_outputs == get(None, None)


def test_get_resources_with_resource_name(mock_provisioned_remote_state: MagicMock):
    """Test get resources function with resource name specified."""
    expected_output = {
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"}
    }

    assert expected_output == get("experiment-tracker", None)

def test_get_resources_resource_name_with_capitals(mock_provisioned_remote_state: MagicMock):
    """Test get resources with a resource name containing errant capital letter(s)."""
    expected_output = {
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"}
    }
    assert expected_output == get("Experiment-tracker", None)


def test_get_resources_with_invalid_resource_name(
    mock_provisioned_remote_state: MagicMock,
):
    """Test get resources function with an invalid resource name specified.

    Args:
        mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
    """
    with pytest.raises(MatchaInputError):
        get("invalid-resource", None)


def test_get_resources_with_resource_name_and_property_name(
    mock_provisioned_remote_state: MagicMock,
):
    """Test get resources function with resource name and resource property specified.

    Args:
        mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
    """
    expected_output = {"experiment-tracker": {"tracking-url": "mlflow_test_url"}}

    assert expected_output == get("experiment-tracker", "tracking-url")


def test_get_resources_with_resource_and_property_names_with_capitals(
        mock_provisioned_remote_state: MagicMock
):
    expected_output = {"experiment-tracker": {"tracking-url": "mlflow_test_url"}}
    assert expected_output == get("Experiment-tracker", "TRacking-url")

def test_opt_out_subcommand(
    runner,
    matcha_testing_directory: str,
    expected_configuration: Dict[str, Union[str, bool]],
) -> None:
    """Test opt-out command works.

    Args:
        runner: Mock runner
        matcha_testing_directory (str): Temp directory
        expected_configuration (Dict[str, Union[str, bool]]): Dictionary containing expected configuration
    """
    config_file_path = os.path.join(
        matcha_testing_directory, ".matcha-ml", "config.yaml"
    )

    expected_configuration["analytics_opt_out"] = True

    # Check if config file is not present
    assert not os.path.exists(config_file_path)

    with mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.default_config_file_path",
        new_callable=mock.PropertyMock,
    ) as file_path, mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.user_id",
        new_callable=mock.PropertyMock,
    ) as uid:
        file_path.return_value = config_file_path
        uid.return_value = "dummy_user_id"
        result = runner.invoke(app, ["analytics", "opt-out"])

        # Check if running command is success
        assert result.exit_code == 0

    # Check if config file is present
    assert os.path.exists(config_file_path)

    # Check the contents of the config file match
    with open(config_file_path) as f:
        assert dict(yaml.safe_load(f)) == expected_configuration


def test_opt_in_subcommand(
    runner,
    matcha_testing_directory: str,
    expected_configuration: Dict[str, Union[str, bool]],
) -> None:
    """Test opt-in command works.

    Args:
        runner: Mock runner
        matcha_testing_directory (str): Temp directory
        expected_configuration (Dict[str, Union[str, bool]]): Dictionary containing expected configuration
    """
    config_file_path = os.path.join(
        matcha_testing_directory, ".matcha-ml", "config.yaml"
    )

    # Check if config file is not present
    assert not os.path.exists(config_file_path)

    with mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.default_config_file_path",
        new_callable=mock.PropertyMock,
    ) as file_path, mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.user_id",
        new_callable=mock.PropertyMock,
    ) as uid:
        file_path.return_value = config_file_path
        uid.return_value = "dummy_user_id"
        result = runner.invoke(app, ["analytics", "opt-in"])

        # Check if running command is success
        assert result.exit_code == 0

    # Check if config file is present
    assert os.path.exists(config_file_path)

    # Check the contents of the config file match
    with open(config_file_path) as f:
        assert dict(yaml.safe_load(f)) == expected_configuration


def test_remove_state_lock_function(mock_provisioned_remote_state: MagicMock):
    """Test that the unlock function is called once when emove_state_lock function is used.

    Args:
        mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
    """
    # with mock.patch("matcha_ml.core.core.RemoteStateManager.unlock") as mock_unlock:
    remove_state_lock()

    # Check if unlock function from RemoteStateManager class is called only once
    mock_provisioned_remote_state.unlock.assert_called_once()


def test_remove_state_lock_function_warning(
    mock_azure_storage_instance: MagicMock, mock_provisioned_remote_state: MagicMock
):
    """Test that the unlock function is called once when emove_state_lock function is used.

    Args:
        mock_azure_storage_instance (MagicMock): mock of an AzureStorage instance
        mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
    """
    mock_azure_storage_instance.blob_exists.return_value = False
    mock_azure_storage_instance.delete_blob.side_effect = Exception("Does not exist")

    remove_state_lock()

    # Check if delete_blob function from AzureStorage class is not called
    mock_azure_storage_instance.delete_blob.assert_not_called()

    # Check if unlock function from RemoteStateManager class is called only once
    mock_provisioned_remote_state.unlock.assert_called_once()
