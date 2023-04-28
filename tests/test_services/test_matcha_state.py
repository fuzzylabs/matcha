"""Tests for Terraform Service."""
import json
import os

import pytest

from matcha_ml.services.matcha_state import MatchaStateService


@pytest.fixture
def matcha_state_service() -> MatchaStateService:
    """Return a template runner object instance for test.

    Returns:
        TemplateRunner: a TemplateRunner object instance.
    """
    return MatchaStateService()


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
        "model-deployer": {
            "flavor": "seldon",
            "base-url": "test_seldon_base_url",
            "workloads-namespace": "test_seldon_workloads_namespace",
        },
        "orchestrator": {"flavor": "aks", "k8s-context": "k8s_test_context"},
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "zenml_test_connection_string",
            "server-password": "zen_server_password",
            "server-url": "zen_server_url",
            "server-username": "zen_server_username",
            "storage-path": "zenml_test_storage_path",
        },
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
        "model-deployer": {
            "flavor": "seldon",
            "base-url": "test_seldon_base_url",
            "workloads-namespace": "test_seldon_workloads_namespace",
        },
        "orchestrator": {"flavor": "aks", "k8s-context": "k8s_test_context"},
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "zenml_test_connection_string",
            "server-password": "zen_server_password",
            "server-url": "zen_server_url",
            "server-username": "zen_server_username",
            "storage-path": "zenml_test_storage_path",
        },
    }

    return outputs


def test_state_file(matcha_state_service: MatchaStateService, expected_outputs: dict):
    """Test whether the state file getter behaves and return as expected.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
        expected_outputs (dict): The expected state file.
    """
    result = matcha_state_service._state_file
    assert result == expected_outputs


def test_fetch_resources_from_state_file(
    matcha_state_service: MatchaStateService, expected_outputs: dict
):
    """Test whether the fetch_resources_from_state_file function is able to return resource specified by the resource name.

    This also test whether it is able to return all resources when no resource name is specified.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
        expected_outputs (dict): The expected state file.
    """
    _ = matcha_state_service.check_state_file_exists()

    result = matcha_state_service.fetch_resources_from_state_file()
    assert result == expected_outputs

    result = matcha_state_service.fetch_resources_from_state_file(
        resource_name="experiment-tracker", property_name="tracking-url"
    )
    expected = {"experiment-tracker": {"tracking-url": "mlflow_test_url"}}
    assert result == expected
