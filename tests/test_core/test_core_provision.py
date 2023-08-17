"""Test suite to test the core matcha provision function."""
import glob
import json
import os
import uuid
from pathlib import Path
from typing import Dict, Iterator, Union
from unittest import mock
from unittest.mock import MagicMock

import pytest

from matcha_ml.core import provision
from matcha_ml.core._validation import LONGEST_RESOURCE_NAME, MAXIMUM_RESOURCE_NAME_LEN
from matcha_ml.core.core import infer_zenml_version
from matcha_ml.errors import MatchaError, MatchaInputError
from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.state.matcha_state import (
    MatchaState,
)
from matcha_ml.templates.azure_template import SUBMODULE_NAMES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)

RUN_TWICE = 2

REMOTE_STATE_MANAGER_PREFIX = "matcha_ml.state.remote_state_manager.RemoteStateManager"

INTERNAL_FUNCTION_STUB = "matcha_ml.services.global_parameters_service.GlobalParameters"


@pytest.fixture(autouse=True)
def teardown_singleton():
    """Tears down the singleton before each test case by clearing the current object."""
    GlobalParameters._instance = None


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


@pytest.fixture(autouse=True)
def mock_use_lock():
    """Mock use_lock state context manager."""
    with mock.patch(
        "matcha_ml.core.core.RemoteStateManager.use_lock"
    ) as mocked_use_lock:
        yield mocked_use_lock


@pytest.fixture(autouse=True)
def mock_use_remote_state():
    """Mock use_remote_state state context manager."""
    with mock.patch(
        "matcha_ml.core.core.RemoteStateManager.use_remote_state"
    ) as mocked_use_remote_state:
        yield mocked_use_remote_state


def test_provision_returns_matcha_state(
    matcha_testing_directory: str,
    state_file_as_object: MatchaState,
    uuid_for_testing: uuid.UUID,
):
    """Test that provision returns a MatchaState object.

    Args:
        matcha_testing_directory (str): temporary working directory.
        state_file_as_object (MatchaState): the Matcha state testing fixture.
        uuid_for_testing (uuid.UUID): Fixed UUID4 value.
    """
    os.chdir(matcha_testing_directory)

    with mock.patch(
        "matcha_ml.services.terraform_service.python_terraform.Terraform.output"
    ) as terraform_client_output, mock.patch(
        "matcha_ml.state.matcha_state.uuid.uuid4"
    ) as uuid_mock:
        terraform_client_output.return_value = {
            "cloud_azure_resource_group_name": {
                "value": "test_resources",
            },
            "container_registry_azure_registry_name": {
                "value": "azure_registry_name",
            },
            "container_registry_azure_registry_url": {
                "value": "azure_container_registry",
            },
            "pipeline_zenml_connection_string": {
                "value": "zenml_test_connection_string",
            },
            "pipeline_zenml_server_password": {
                "value": "zen_server_password",
            },
            "pipeline_zenml_server_url": {
                "value": "zen_server_url",
            },
            "experiment_tracker_mlflow_tracking_url": {
                "value": "mlflow_test_url",
            },
        }
        uuid_mock.return_value = uuid_for_testing
        provision_result = provision(
            location="ukwest", prefix="test", password="default"
        )

    assert isinstance(state_file_as_object, MatchaState)
    assert provision_result == state_file_as_object


def assert_infrastructure(
    destination_path: str,
    expected_tf_vars: Dict[str, str],
    check_matcha_state_file: bool = True,
):
    """Assert if the infrastructure configuration is valid.

    Args:
        destination_path (str): infrastructure config destination path
        expected_tf_vars (Dict[str, str]): expected Terraform variables
        check_matcha_state_file (bool): whether to check the matcha.state file exists and have correct value. Defaults to True.
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

    if check_matcha_state_file:
        # Check that matcha state file exists and content is equal/correct
        state_file_path = os.path.join(destination_path, os.pardir, "matcha.state")
        assert os.path.exists(state_file_path)

        with open(state_file_path) as f:
            tf_vars = json.load(f)

        _ = expected_tf_vars.pop("password", None)
        expected_matcha_state_vars = {"cloud": expected_tf_vars}
        assert tf_vars == expected_matcha_state_vars


def test_provision_copies_infrastructure_templates_with_specified_values(
    matcha_testing_directory: str, mock_use_lock: MagicMock
):
    """Test provision command copies the infrastructure template with specified location and prefix values.

    Args:
        matcha_testing_directory (str): temporary working directory
        mock_use_lock (MagicMock): mock use_lock context manager
    """
    os.chdir(matcha_testing_directory)

    _ = provision("uksouth", "coffee", "default")

    state_storage_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "remote_state_storage"
    )

    resources_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure", "resources"
    )

    state_storage_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "coffee",
    }

    resources_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "coffee",
        "password": "default",
        "zenmlserver_version": "latest",
    }

    assert_infrastructure(
        state_storage_destination_path, state_storage_expected_tf_vars, False
    )
    assert_infrastructure(resources_destination_path, resources_expected_tf_vars, False)
    mock_use_lock.assert_called_once()


@pytest.mark.parametrize(
    "location, prefix, expected_output",
    [
        (
            "uksouth",
            "-matcha",
            "Resource group name prefix can only contain alphanumeric characters.",
        ),
        (
            "uksouth",
            "12",
            "Resource group name prefix cannot contain only numbers.",
        ),
        (
            "uksouth",
            "good$prefix#",
            "Resource group name prefix can only contain alphanumeric characters.",
        ),
        (
            "uksouth",
            "areallylongprefix",
            f"Resource group name prefix must be between 3 and {MAXIMUM_RESOURCE_NAME_LEN - len(LONGEST_RESOURCE_NAME)} characters long.",
        ),
    ],
)
def test_provision_raises_exception_for_invalid_prefixes(
    mock_state_file: Path,
    matcha_testing_directory: str,
    mock_use_lock: MagicMock,
    location: str,
    prefix: str,
    expected_output: str,
):
    """Test whether the prefix validation function prompt an error message when user entered an invalid prefix.

    Args:
        mock_state_file (Path): a mocked state file
        matcha_testing_directory (str): temporary working directory
        mock_use_lock (MagicMock): mock use_lock context manager
        location (str): provisioning location
        prefix (str): Azure resource group prefix name
        expected_output (str): the expected error message
    """
    os.chdir(matcha_testing_directory)
    with pytest.raises(MatchaInputError) as e:
        _ = provision(location, prefix, password="default")

    assert expected_output in str(e)
    mock_use_lock.assert_not_called()


def test_provision_with_provisioned_resources(
    matcha_testing_directory: str, mock_state_file: Path
):
    """Test provision command when there are already existing resources deployed.

    Args:
        matcha_testing_directory (str): temporary working directory.
        mock_state_file (Path): a mocked state file
    """
    # change to matcha testing directory
    os.chdir(matcha_testing_directory)

    # we need to mock an Azure deployment already exists
    with mock.patch(
        f"{REMOTE_STATE_MANAGER_PREFIX}.is_state_provisioned"
    ) as is_state_provisioned:
        is_state_provisioned.return_value = True

        # the result here should be that Matcha exits displaying a warning that the resources are already provisioned
        with pytest.raises(MatchaError) as e:
            _ = provision(location="uksouth", prefix="matcha", password="default")

    assert (
        "Error - Matcha has detected that there are resources already provisioned."
        in str(e)
    )


def test_stale_remote_state_file_is_removed(matcha_testing_directory: str):
    """Test.

    Args:
        matcha_testing_directory (str): temporary working directory.
    """
    os.chdir(matcha_testing_directory)

    # Add stale config file
    config_file_contents = {
        "remote_state_bucket": {
            "account_name": "matcha-account",
            "container_name": "matcha-container",
            "resource_group_name": "matcha-rg",
        }
    }
    with open("matcha.config.json", "w") as f:
        json.dump(config_file_contents, f)

    expected_config_file_contents = {
        "remote_state_bucket": {
            "account_name": "test-account",
            "container_name": "test-container",
            "resource_group_name": "test-rg",
        }
    }

    with mock.patch(
        f"{REMOTE_STATE_MANAGER_PREFIX}._resource_group_exists"
    ) as is_rg_provisioned:
        is_rg_provisioned.return_value = False
        _ = provision(location="uksouth", prefix="test", password="default")

    with open("matcha.config.json") as f:
        config_file_contents = json.load(f)

    assert expected_config_file_contents == config_file_contents


def test_version_inference_latest():
    """Test checking when zenml isn't installed, the latest version is returned."""
    assert infer_zenml_version() == "latest"
