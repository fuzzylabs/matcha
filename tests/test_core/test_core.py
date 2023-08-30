"""Test suite to test the core matcha commands and all its subcommands."""
import json
import os
import uuid
from pathlib import Path
from typing import Dict, Iterable, Iterator, Union
from unittest import mock
from unittest.mock import MagicMock

import pytest
import yaml

from matcha_ml.cli.cli import app
from matcha_ml.config.matcha_config import (
    MatchaConfig,
    MatchaConfigComponentProperty,
    MatchaConfigService,
)
from matcha_ml.core import get, remove_state_lock
from matcha_ml.core.core import stack_add, stack_remove
from matcha_ml.errors import MatchaError, MatchaInputError
from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.state.matcha_state import (
    MatchaState,
    MatchaStateComponent,
)

INTERNAL_FUNCTION_STUB = "matcha_ml.services.global_parameters_service.GlobalParameters"


@pytest.fixture(autouse=True)
def mock_state_file_wrapper(mock_state_file: Path) -> Path:
    """Re-use fixture from conftest.py with autouse instead.

    A fixture for mocking a test state file in the test directory.

    Args:
        mock_state_file (Path): Path to mocked matcha.state file

    Yields:
        Path: Path object to matcha.state file
    """
    yield mock_state_file


@pytest.fixture
def experiment_tracker_state_component(
    state_file_as_object: MatchaState,
) -> MatchaStateComponent:
    """A single state component as a fixture, specifically, the experiment-tracker.

    Args:
        state_file_as_object (MatchaState): the expected MatchaState fixture.

    Returns:
        MatchaStateComponent: the experiment tracker state component.
    """
    return state_file_as_object.components[-2]


@pytest.fixture(autouse=True)
def teardown_singleton():
    """Tears down the singleton before each test case by clearing the current object."""
    GlobalParameters._instance = None


@pytest.fixture(autouse=True)
def mock_provisioned_remote_state(uuid_for_testing: uuid.UUID) -> Iterable[MagicMock]:
    """Mock remote state manager to have state provisioned.

    Returns:
        MagicMock: mock of a RemoteStateManager instance
    """
    with mock.patch(
        "matcha_ml.core.core.RemoteStateManager"
    ) as mock_state_manager_class:
        mock_state_manager = mock_state_manager_class.return_value
        mock_state_manager.is_state_provisioned.return_value = True
        mock_state_manager.get_hash_remote_state.return_value = (
            "470544910b3fe623e00d63e6314588a3"
        )

        def download(path):
            state_file_resources = {
                "cloud": {"flavor": "azure", "resource-group-name": "test_resources"},
                "container-registry": {
                    "flavor": "azure",
                    "registry-name": "azure_registry_name",
                    "registry-url": "azure_container_registry",
                },
                "pipeline": {
                    "flavor": "zenml",
                    "connection-string": "zenml_test_connection_string",
                    "server-password": "zen_server_password",
                    "server-url": "zen_server_url",
                },
                "experiment-tracker": {
                    "flavor": "mlflow",
                    "tracking-url": "mlflow_test_url",
                },
                "id": {"matcha_uuid": str(uuid_for_testing)},
            }
            with open(".matcha/infrastructure/matcha.state", "w") as f:
                json.dump(state_file_resources, f)

        mock_state_manager.download = download
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
    mock_provisioned_remote_state: MagicMock, state_file_as_object: MatchaState
):
    """Test get resources function with no resource specified.

    Args:
        mock_provisioned_remote_state (MagicMock): mock of a RemoteStateManager instance
        state_file_as_object (MatchaState): the expected MatchaState fixture.
    """
    assert state_file_as_object == get(None, None)


def test_get_resources_resource_name_with_capitals(
    mock_provisioned_remote_state: MagicMock,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test get resources with a resource name containing errant capital letter(s).

    Args:
        mock_provisioned_remote_state (MagicMock): mock of a RemoteStateManager instance.
        experiment_tracker_state_component (MatchaStateComponent): the experiment tracker state components.
    """
    get_result = get(resource_name="Experiment-Tracker", property_name=None)

    assert get_result and len(get_result.components) == 1

    assert get_result.components[0] == experiment_tracker_state_component


def test_get_resources_with_resource_name(
    mock_provisioned_remote_state: MagicMock,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test get resources function with resource name specified.

    Args:
        mock_provisioned_remote_state (MagicMock): mock of a RemoteStateManager instance
        experiment_tracker_state_component (MatchaStateComponent): the experiment tracker state component.
    """
    get_result = get(resource_name="experiment-tracker", property_name=None)

    assert get_result and len(get_result.components) == 1

    assert get_result.components[0] == experiment_tracker_state_component


def test_get_resources_with_resource_name_and_property_name(
    mock_provisioned_remote_state: MagicMock,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test get resources function with resource name and resource property specified.

    Args:
        mock_provisioned_remote_state (MagicMock): mock of a RemoteStateManager instance.
        experiment_tracker_state_component (MatchaStateComponent): the experiment tracker state component.
    """
    get_result = get(resource_name="experiment-tracker", property_name="flavor")

    assert get_result and len(get_result.components) == 1

    assert (
        get_result.components[0].properties[0]
        == experiment_tracker_state_component.properties[0]
    )


def test_get_resources_with_invalid_resource_name(
    mock_provisioned_remote_state: MagicMock,
):
    """Test get resources function with an invalid resource name specified.

    Args:
        mock_provisioned_remote_state (MagicMock): mock of a RemoteStateManager instance
    """
    with pytest.raises(MatchaInputError):
        get("invalid-resource", None)


def test_get_resources_with_resource_and_property_names_with_capitals(
    mock_provisioned_remote_state: MagicMock,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test get resources function with resource name and resource property specified with arguments containing errant capital letter(s).

    Args:
        mock_provisioned_remote_state (MagicMock): mock of a RemoteStateManager instance.
        experiment_tracker_state_component (MatchaStateComponent): the experiment tracker state component.
    """
    get_result = get(resource_name="Experiment-Tracker", property_name="Flavor")

    assert get_result and len(get_result.components) == 1

    assert (
        get_result.components[0].properties[0]
        == experiment_tracker_state_component.properties[0]
    )


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
    """Test that the unlock function is called once when remove_state_lock function is used.

    Args:
        mock_provisioned_remote_state (MagicMock): mock of a RemoteStateManager instance
    """
    remove_state_lock()

    # Check if unlock function from RemoteStateManager class is called only once
    mock_provisioned_remote_state.unlock.assert_called_once()


def test_remove_state_lock_function_warning(
    mock_azure_storage_instance: MagicMock, mock_provisioned_remote_state: MagicMock
):
    """Test that the unlock function is called once when remove_state_lock function is used.

    Args:
        mock_azure_storage_instance (MagicMock): mock of an AzureStorage instance
        mock_provisioned_remote_state (MagicMock): mock of a RemoteStateManager instance
    """
    mock_azure_storage_instance.blob_exists.return_value = False
    mock_azure_storage_instance.delete_blob.side_effect = Exception("Does not exist")

    remove_state_lock()

    # Check if delete_blob function from AzureStorage class is not called
    mock_azure_storage_instance.delete_blob.assert_not_called()

    # Check if unlock function from RemoteStateManager class is called only once
    mock_provisioned_remote_state.unlock.assert_called_once()


def test_get_downloads_matcha_state_directory(mock_state_file, state_file_as_object):
    """Test that get downloads the matcha state directory when it does not exist locally for a user and does exist remotely.

    Args:
        mock_state_file (Path): Path to mocked matcha.state file
        state_file_as_object (MatchaState): the expected MatchaState fixture.
    """
    state_file_location = os.path.join(os.getcwd(), mock_state_file)
    # Remove matcha.state file
    os.remove(state_file_location)
    assert not os.path.exists(state_file_location)

    # Run get and expect the matcha.state file to have been redownloaded
    get_result = get(None, None)

    assert os.path.exists(state_file_location)
    assert state_file_as_object == get_result


def test_stack_add_expected(matcha_testing_directory: str):
    """Tests that the core stack_add function works as expected for a given input.

    Args:
        matcha_testing_directory (str): Mock directory for testing.
    """
    os.chdir(matcha_testing_directory)

    with mock.patch(
        "matcha_ml.core.core.RemoteStateManager"
    ) as provisioned_state, mock.patch(
        "matcha_ml.core.core.MatchaConfigService.add_property"
    ) as add_property:
        mock_remote_state_manager = MagicMock()
        provisioned_state.return_value = mock_remote_state_manager
        mock_remote_state_manager.is_state_provisioned.return_value = False
        add_property.return_value = None

        stack_add(module_type="experiment_tracker", module_flavor="mlflow")

        add_property.assert_has_calls(
            [
                mock.call(
                    "stack",
                    MatchaConfigComponentProperty(
                        name="experiment_tracker", value="mlflow"
                    ),
                ),
                mock.call(
                    "stack", MatchaConfigComponentProperty(name="name", value="custom")
                ),
            ]
        )


def test_stack_add_invalid_flavor(matcha_testing_directory: str):
    """Tests that the core stack_add function raises an exception when a flavor is invalid.

    Args:
        matcha_testing_directory (str): Mock directory for testing.
    """
    os.chdir(matcha_testing_directory)

    with mock.patch(
        "matcha_ml.core.core.RemoteStateManager"
    ) as provisioned_state, mock.patch(
        "matcha_ml.core.core.MatchaConfigService.add_property"
    ) as add_property:
        mock_remote_state_manager = MagicMock()
        provisioned_state.return_value = mock_remote_state_manager
        mock_remote_state_manager.is_state_provisioned.return_value = False
        add_property.return_value = None

        with pytest.raises(MatchaInputError) as e:
            stack_add(module_type="experiment_tracker", module_flavor="flavor")

        assert (
            "The module type 'experiment_tracker' does not have a flavor 'flavor'."
            in str(e)
        )


def test_stack_add_invalid_module_type(matcha_testing_directory: str):
    """Tests that the core stack_add function raises an exception when a module type is invalid.

    Args:
        matcha_testing_directory (str): Mock directory for testing.
    """
    os.chdir(matcha_testing_directory)

    with mock.patch(
        "matcha_ml.core.core.RemoteStateManager"
    ) as provisioned_state, mock.patch(
        "matcha_ml.core.core.MatchaConfigService.add_property"
    ) as add_property:
        mock_remote_state_manager = MagicMock()
        provisioned_state.return_value = mock_remote_state_manager
        mock_remote_state_manager.is_state_provisioned.return_value = False
        add_property.return_value = None

        with pytest.raises(MatchaInputError) as e:
            stack_add(module_type="invalid_module", module_flavor="flavor")

        assert "The module type 'invalid_module' does not exist." in str(e)


def test_stack_add_with_existing_deployment(matcha_testing_directory: str):
    """Tests that the core stack_add function raises an exception when a deployment already exists.

    Args:
        matcha_testing_directory (str): Mock directory for testing.
    """
    os.chdir(matcha_testing_directory)

    with mock.patch(
        "matcha_ml.core.core.RemoteStateManager"
    ) as provisioned_state, mock.patch(
        "matcha_ml.core.core.MatchaConfigService.add_property"
    ) as add_property:
        mock_remote_state_manager = MagicMock()
        provisioned_state.return_value = mock_remote_state_manager
        mock_remote_state_manager.is_state_provisioned.return_value = True
        add_property.return_value = None

        with pytest.raises(MatchaError) as e:
            stack_add(module_type="invalid_module", module_flavor="flavor")

        assert (
            "The remote resources are already provisioned. Changing the stack now will not change the remote state."
            in str(e)
        )


def test_stack_remove_with_state_provisioned(matcha_testing_directory):
    """Tests that the core stack_remove function raises an exception when a deployment already exists.

    Args:
        matcha_testing_directory (str): Mock directory for testing.
    """
    os.chdir(matcha_testing_directory)

    with mock.patch("matcha_ml.core.core.RemoteStateManager") as provisioned_state:
        mock_remote_state_manager = MagicMock()
        mock_remote_state_manager.is_state_provisioned.return_value = True
        provisioned_state.return_value = mock_remote_state_manager

        with pytest.raises(MatchaError) as e:
            stack_remove(module_type="test_module")

        assert (
            "The remote resources are already provisioned. Changing the stack now will not change the remote state."
            in str(e)
        )


def test_stack_remove_with_module_present(
    matcha_testing_directory: str, mocked_matcha_config: MatchaConfig
):
    """Tests that the core stack_remove function removes a module when then module exists.

    Args:
        matcha_testing_directory (str): Mock directory for testing.
        mocked_matcha_config (MatchaConfig): A mocked MatchaConfig object for testing.
    """
    os.chdir(matcha_testing_directory)
    MatchaConfigService.write_matcha_config(mocked_matcha_config)

    with mock.patch("matcha_ml.core.core.RemoteStateManager") as provisioned_state:
        mock_remote_state_manager = MagicMock()
        mock_remote_state_manager.is_state_provisioned.return_value = False
        provisioned_state.return_value = mock_remote_state_manager
        stack_remove(module_type="experiment_tracker")

    new_matcha_config = MatchaConfigService.read_matcha_config()

    new_matcha_config.to_dict()
    mocked_matcha_config.to_dict()

    assert mocked_matcha_config.find_component(
        "remote_state_bucket"
    ) == new_matcha_config.find_component("remote_state_bucket")
    assert (
        new_matcha_config.find_component("stack").find_property("name").value
        == "custom"
    )
    assert not new_matcha_config.find_component("stack").find_property(
        "experiment_tracker"
    )


def test_stack_remove_with_no_module(
    matcha_testing_directory: str, mocked_matcha_config: MatchaConfig
):
    """Tests that the core stack_remove function raises an exception when a module does not exist.

    Args:
        matcha_testing_directory (str): Mock directory for testing.
        mocked_matcha_config (MatchaConfig): A mocked MatchaConfig object for testing.
    """
    os.chdir(matcha_testing_directory)
    MatchaConfigService.write_matcha_config(mocked_matcha_config)

    with mock.patch(
        "matcha_ml.core.core.RemoteStateManager"
    ) as provisioned_state, pytest.raises(MatchaInputError) as e:
        mock_remote_state_manager = MagicMock()
        mock_remote_state_manager.is_state_provisioned.return_value = False
        provisioned_state.return_value = mock_remote_state_manager
        stack_remove(module_type="test_module")

        assert "Module 'test_module' does not exist in the current stack." in str(e)
