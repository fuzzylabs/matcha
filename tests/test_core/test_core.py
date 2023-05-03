"""Test suite to test the core matcha commands and all its subcommands."""
import json
import os

import pytest

from matcha_ml.core.core import get


@pytest.fixture(autouse=True)
def mock_state_file(matcha_testing_directory: str):
    """A fixture for mocking a test state file in the test directory.

    Args:
        matcha_testing_directory (str): the test directory
    """
    os.chdir(matcha_testing_directory)

    matcha_infrastructure_dir = os.path.join(".matcha", "infrastructure")
    os.makedirs(matcha_infrastructure_dir)

    state_file_resources = {
        "cloud": {"flavor": "azure", "resource-group-name": "test_resources"},
        "container-registry": {
            "flavor": "azure",
            "registry-name": "azure_registry_name",
            "registry-url": "azure_container_registry",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
    }

    with open(os.path.join(matcha_infrastructure_dir, "matcha.state"), "w") as f:
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


def test_get_resources(expected_outputs: dict):
    """Test get resources function with no resource specified.

    Args:
        expected_outputs (dict): The expected output from the matcha state file.
    """
    assert expected_outputs == get(None, None)


def test_get_resources_with_resource_name():
    """Test get resources function with resource name specified."""
    expected_output = {
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"}
    }

    assert expected_output == get("experiment-tracker", None)


def test_get_resources_with_resource_name_and_property_name():
    """Test get resources function with resource name and resource property specified."""
    expected_output = {"experiment-tracker": {"tracking-url": "mlflow_test_url"}}

    assert expected_output == get("experiment-tracker", "tracking-url")
