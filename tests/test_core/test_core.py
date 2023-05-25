"""Test suite to test the core matcha commands and all its subcommands."""
import json
import os
from typing import Dict, Union
from unittest import mock

import pytest
import yaml

from matcha_ml.cli.cli import app
from matcha_ml.core.core import get
from matcha_ml.errors import MatchaError, MatchaInputError
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


@pytest.fixture
def expected_configuration() -> Dict[str, Union[str, bool]]:
    """Pytest fixture to return expected configuration.

    Returns:
        Dict[str, Union[str, bool]]: Dictionary containing expected configuration
    """
    return {"analytics_opt_out": False, "user_id": "dummy_user_id"}


def test_get_resources(expected_outputs: dict):
    """Test get resources function with no resource specified.

    Args:
        expected_outputs (dict): The expected output from the matcha state file.
    """
    assert expected_outputs == get(None, None)


def test_get_resources_without_state_file():
    """Test get resources function when a state file does not exist."""
    state_file_path = os.path.join(".matcha", "infrastructure", "matcha.state")
    os.remove(state_file_path)

    with pytest.raises(MatchaError):
        get(None, None)


def test_get_resources_with_resource_name():
    """Test get resources function with resource name specified."""
    expected_output = {
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"}
    }

    assert expected_output == get("experiment-tracker", None)


def test_get_resources_with_invalid_resource_name():
    """Test get resources function with an invalid resource name specified."""
    with pytest.raises(MatchaInputError):
        get("invalid-resource", None)


def test_get_resources_with_resource_name_and_property_name():
    """Test get resources function with resource name and resource property specified."""
    expected_output = {"experiment-tracker": {"tracking-url": "mlflow_test_url"}}

    assert expected_output == get("experiment-tracker", "tracking-url")


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
