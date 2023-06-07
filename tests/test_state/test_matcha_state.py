"""Tests for Matcha State Service."""
import json
import os

import pytest

from matcha_ml.state import MatchaStateService
from matcha_ml.state.matcha_state import (
    MatchaResource,
    MatchaResourceProperty,
    MatchaState,
    MatchaStateComponent,
)


@pytest.fixture
def matcha_state_service() -> MatchaStateService:
    """Return a matcha state service object instance for test.

    Returns:
        MatchaStateService: a MatchaStateService object instance.
    """
    return MatchaStateService()


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


@pytest.fixture
def state_file_as_object() -> MatchaState:
    """A fixture to represent the Matcha state as a MatchaState object.

    Returns:
        MatchaState: the Matcha state testing fixture.
    """
    return MatchaState(
        components=[
            MatchaStateComponent(
                resource=MatchaResource("cloud"),
                properties=[
                    MatchaResourceProperty("flavor", "azure"),
                    MatchaResourceProperty("resource-group-name", "test_resources"),
                ],
            ),
            MatchaStateComponent(
                resource=MatchaResource("container-registry"),
                properties=[
                    MatchaResourceProperty("flavor", "azure"),
                    MatchaResourceProperty("registry-name", "azure_registry_name"),
                    MatchaResourceProperty("registry-url", "azure_container_registry"),
                ],
            ),
            MatchaStateComponent(
                resource=MatchaResource("experiment-tracker"),
                properties=[
                    MatchaResourceProperty("flavor", "mlflow"),
                    MatchaResourceProperty("tracking-url", "mlflow_test_url"),
                ],
            ),
        ]
    )


@pytest.fixture
def experiment_tracker_state_component() -> MatchaStateComponent:
    """A single state component as a fixture, specifically, the experiment-tracker.

    Returns:
        MatchaStateComponent: the experiment tracker state component.
    """
    return MatchaStateComponent(
        resource=MatchaResource("experiment-tracker"),
        properties=[
            MatchaResourceProperty("flavor", "mlflow"),
            MatchaResourceProperty("tracking-url", "mlflow_test_url"),
        ],
    )


def test_state_file_getter(
    matcha_state_service: MatchaStateService, expected_outputs: dict
):
    """Test whether the state file getter behaves and return as expected.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
        expected_outputs (dict): The expected state file.
    """
    result = matcha_state_service.state_file
    assert result == expected_outputs


def test_fetch_resources_from_state_file_full(
    matcha_state_service: MatchaStateService, state_file_as_object: MatchaState
):
    """Test whether the fetch_resources_from_state_file function is able to return resource specified by the resource name.

    This also test whether it is able to return all resources when no resource name is specified.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
        state_file_as_object (MatchaState): The state file represented as a MatchaState object.
    """
    state = matcha_state_service.fetch_resources_from_state_file()
    assert state == state_file_as_object


def test_fetch_resources_from_state_file_resource_only(
    matcha_state_service: MatchaStateService,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test whether fetching resources just using the resource name returns the expected result.

    Args:
        matcha_state_service (MatchaStateService): The Matcha state service testing instance.
        experiment_tracker_state_component (MatchaStateComponent): The experiment tracker state componment testing fixture.
    """
    property = matcha_state_service.fetch_resources_from_state_file(
        resource_name="experiment-tracker", property_name=None
    )

    assert property.components and len(property.components) == 1

    assert property.components[0] == experiment_tracker_state_component


def test_fetch_resources_from_state_file_with_resource_and_property(
    matcha_state_service: MatchaStateService,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test whether fetching resources using both the resource name and property name returns the expected result.

    Args:
        matcha_state_service (MatchaStateService): The Matcha state service testing instance.
        experiment_tracker_state_component (MatchaStateComponent): The experiment tracker state component testing fixture.
    """
    state = matcha_state_service.fetch_resources_from_state_file(
        resource_name="experiment-tracker", property_name="flavor"
    )
    assert state.components and len(state.components) == 1

    assert (
        state.components[0].properties[0]
        == experiment_tracker_state_component.properties[0]
    )


def test_check_state_file_exists(matcha_state_service: MatchaStateService):
    """Test check state file returns True when matcha state file exists.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
    """
    result = matcha_state_service.check_state_file_exists()
    assert result is True


def test_check_state_file_does_not_exist(matcha_state_service: MatchaStateService):
    """Test check state file returns False when matcha state file does not exist.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
    """
    matcha_state_path = os.path.join(".matcha", "infrastructure", "matcha.state")

    os.remove(matcha_state_path)

    result = matcha_state_service.check_state_file_exists()
    assert result is False


def test_get_hash_local_state(matcha_state_service: MatchaStateService):
    """Test get hash of the local state file.

    Args:
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
    """
    expected_hash = "031318ef84db0275c7d26230a51eb459"
    result_hash = matcha_state_service.get_hash_local_state()

    assert result_hash == expected_hash


def test_get_resource_names_expected(matcha_state_service: MatchaStateService):
    """Test that getting the resource names returns the expected results.

    Args:
        matcha_state_service (MatchaStateService): The Matcha state service testing instance.
    """
    assert "cloud" in matcha_state_service.get_resource_names()


def test_get_resource_names_resource_not_present(
    matcha_state_service: MatchaStateService,
):
    """Test that the correct names are being returned by the get resource names function.

    Args:
        matcha_state_service (MatchaStateService): The Matcha state service testing instance.
    """
    assert "not a resource" not in matcha_state_service.get_resource_names()


def test_convert_to_matcha_state_object(
    matcha_state_service: MatchaStateService, state_file_as_object: MatchaState
):
    """Test that converting the Matcha state to a MatchaState object works as expected.

    Args:
        matcha_state_service (MatchaStateService): The Matcha state service testing instance.
        state_file_as_object (MatchaState): The Matcha state as a MatchaState object.
    """

    def _compare_object(
        matcha_state_component: MatchaStateComponent, expected: MatchaStateComponent
    ) -> bool:
        """A utility function to test equality between two MatchaStateComponent objects.

        Args:
            matcha_state_component (MatchaStateComponent): the object being tested.
            expected (MatchaStateComponent): the ground truth object.

        Returns:
            bool: True if they are equal, false otherwise.
        """
        return matcha_state_component == expected

    state_object = matcha_state_service._convert_to_matcha_state_object(
        matcha_state_service.state_file
    )

    for state_actual, state_expected in zip(
        state_object.components, state_file_as_object.components
    ):
        assert _compare_object(state_actual, state_expected)
