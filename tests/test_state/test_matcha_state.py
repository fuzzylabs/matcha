"""Tests for Matcha State Service."""
import os
import uuid
from pathlib import Path
from typing import Any

import pytest

from matcha_ml.constants import MATCHA_STATE_PATH
from matcha_ml.errors import MatchaError
from matcha_ml.state import MatchaStateService
from matcha_ml.state.matcha_state import (
    MISSING_STATE_ERROR_MSG,
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
        "id": {"matcha_uuid": "bdd640fb-0667-4ad1-9c80-317fa3b1799d"},
    }

    return outputs


@pytest.fixture
def state_file_as_object(uuid_for_testing: uuid.UUID) -> MatchaState:
    """A fixture to represent the Matcha state as a MatchaState object.

    Args:
        uuid_for_testing (uuid.UUID): Fixted valid UUID for testing.

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
            MatchaStateComponent(
                resource=MatchaResource("id"),
                properties=[
                    MatchaResourceProperty("matcha_uuid", str(uuid_for_testing)),
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


def assert_object(obj: Any, expected_type: Any) -> None:
    """Utility function for asserting that an object isn't None and of the correct type.

    Args:
        obj (Any): the object under test
        expected_type (Any): the expected type of the object
    """
    assert obj is not None
    assert isinstance(obj, expected_type)


def test_state_service_initialisation(
    mock_state_file: Path, state_file_as_object: MatchaState
):
    """Test that object initialisation works as expected when a state file exists.

    Args:
        mock_state_file (Path): a mocked state file in the test directory
        state_file_as_object (MatchaState): the state file as a MatchState instance
    """
    service = MatchaStateService()

    assert_object(service, MatchaStateService)
    assert service._state == state_file_as_object


def test_state_service_initialisation_no_state_file(mock_state_file: Path):
    """Test that object initalisation raises an error when the state file does not exist.

    Args:
        mock_state_file (Path): a mocked state file in the test directory
    """
    os.remove(MATCHA_STATE_PATH)

    with pytest.raises(MatchaError) as err:
        _ = MatchaStateService()

    assert str(err.value) == MISSING_STATE_ERROR_MSG


def test_read_state_expected(mock_state_file: Path, state_file_as_object: MatchaState):
    """Test that reading the state file produces the correct MatchaState object.

    Args:
        mock_state_file (Path): a mocked state file in the test directory
        state_file_as_object (MatchaState): the state file as a MatchaState instance.
    """
    service = MatchaStateService()

    assert_object(service._state, MatchaState)
    assert service._read_state() == state_file_as_object


def test_read_state_no_state_file(mock_state_file: Path):
    """Test that reading the state file raises an error when the state file does not exist.

    Args:
        mock_state_file (Path): a mocked state file in the test directory
    """
    os.remove(MATCHA_STATE_PATH)

    with pytest.raises(MatchaError) as err:
        _ = MatchaStateService()

    assert str(err.value) == MISSING_STATE_ERROR_MSG


def test_fetch_resources_from_state_file_full(
    mock_state_file: Path,
    matcha_state_service: MatchaStateService,
    state_file_as_object: MatchaState,
):
    """Test whether the fetch_resources_from_state_file function is able to return resource specified by the resource name.

    This also test whether it is able to return all resources when no resource name is specified.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
        state_file_as_object (MatchaState): The state file represented as a MatchaState object.
    """
    state = matcha_state_service.fetch_resources_from_state_file()
    assert state == state_file_as_object


def test_fetch_resources_from_state_file_resource_only(
    mock_state_file: Path,
    matcha_state_service: MatchaStateService,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test whether fetching resources just using the resource name returns the expected result.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): The Matcha state service testing instance.
        experiment_tracker_state_component (MatchaStateComponent): The experiment tracker state componment testing fixture.
    """
    property = matcha_state_service.fetch_resources_from_state_file(
        resource_name="experiment-tracker", property_name=None
    )

    assert property.components and len(property.components) == 1

    assert property.components[0] == experiment_tracker_state_component


def test_fetch_resources_from_state_file_with_resource_and_property(
    mock_state_file: Path,
    matcha_state_service: MatchaStateService,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test whether fetching resources using both the resource name and property name returns the expected result.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
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


def test_check_state_file_exists(
    mock_state_file: Path, matcha_state_service: MatchaStateService
):
    """Test check state file returns True when matcha state file exists.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
    """
    result = matcha_state_service.state_exists()
    assert result is True


def test_check_state_file_does_not_exist(
    mock_state_file: Path, matcha_state_service: MatchaStateService
):
    """Test check state file returns False when matcha state file does not exist.

    Args:
        mock_state_file (Path): a mocked state file in the test directory
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
    """
    os.remove(MATCHA_STATE_PATH)

    result = matcha_state_service.state_exists()
    assert result is False


def test_get_hash_local_state(
    mock_state_file: Path, matcha_state_service: MatchaStateService
):
    """Test get hash of the local state file.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): The matcha_state_service testing instance.
    """
    expected_hash = "6ccfbc1dd19dc7692b10f65a9b9bde7c"
    result_hash = matcha_state_service.get_hash_local_state()

    assert result_hash == expected_hash


def test_get_resource_names_expected(
    mock_state_file: Path, matcha_state_service: MatchaStateService
):
    """Test that getting the resource names returns the expected results.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): The Matcha state service testing instance.
    """
    names = matcha_state_service.get_resource_names()

    assert_object(names, list)
    assert "cloud" in matcha_state_service.get_resource_names()


def test_get_resource_names_resource_not_present(
    mock_state_file: Path,
    matcha_state_service: MatchaStateService,
):
    """Test that the correct names are being returned by the get resource names function.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): The Matcha state service testing instance.
    """
    names = matcha_state_service.get_resource_names()

    assert_object(names, list)
    assert "not a resource" not in names


def test_get_property_names_expected(
    mock_state_file: Path, matcha_state_service: MatchaStateService
):
    """Tests that the correct property names are being returned.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): the Matcha state service testing instance.
    """
    names = matcha_state_service.get_property_names(resource_name="cloud")

    assert_object(names, list)
    assert "resource-group-name" in names


def test_get_property_names_not_present(
    mock_state_file: Path, matcha_state_service: MatchaStateService
):
    """Test that the correct property names are being returned.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): the Matcha state service testing instance.
    """
    names = matcha_state_service.get_property_names(resource_name="cloud")

    assert_object(names, list)
    assert "not a property" not in names


def test_matcha_state_to_dict(
    mock_state_file: Path, expected_outputs: dict, state_file_as_object: MatchaState
):
    """Test that converting the MatchState object to a dictionary works as expected.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        expected_outputs (dict): the expected state as a dictionary
        state_file_as_object (MatchaState): the state as a MatchaState object.
    """
    as_dict = state_file_as_object.to_dict()

    assert_object(as_dict, dict)
    assert as_dict == expected_outputs


def test_matcha_state_from_dict(
    mock_state_file: Path, expected_outputs: dict, state_file_as_object: MatchaState
):
    """Test that a MatchaState object can be created from a dictionary.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        expected_outputs (dict): the state as a dictionary
        state_file_as_object (MatchaState): the state as a MatchaState object.
    """
    state = MatchaState.from_dict(state_dict=expected_outputs)

    assert_object(state, MatchaState)
    assert state == state_file_as_object


def test_get_component_expected(
    mock_state_file: Path,
    matcha_state_service: MatchaStateService,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test that a component is found when a valid resource name is given.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): the Matcha state service testing instance.
        experiment_tracker_state_component (MatchaStateComponent): the expected result of the test.
    """
    component = matcha_state_service.get_component(resource_name="experiment-tracker")

    assert_object(component, MatchaStateComponent)
    assert component == experiment_tracker_state_component


def test_get_component_not_found(
    mock_state_file: Path, matcha_state_service: MatchaStateService
):
    """Test that a component which is invalid isn't found and an error is raised.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        matcha_state_service (MatchaStateService): the Matcha state service testing instance.
    """
    invalid_resource_name = "not a resource"
    with pytest.raises(MatchaError) as err:
        _ = matcha_state_service.get_component(resource_name=invalid_resource_name)

    assert (
        str(err.value)
        == "The component with the name 'not a resource' could not be found in the state."
    )


def test_state_component_find_property_expected(
    mock_state_file: Path,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test that a property is found when a valid property name is given to the function.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        experiment_tracker_state_component (MatchaStateComponent): the component used for finding a property.
    """
    expected = experiment_tracker_state_component.properties[0]
    result = experiment_tracker_state_component.find_property(property_name="flavor")

    assert_object(result, MatchaResourceProperty)
    assert result == expected


def test_state_component_find_property_not_found(
    mock_state_file: Path,
    experiment_tracker_state_component: MatchaStateComponent,
):
    """Test that a property which is invalid isn't found and an error is raised.

    Args:
        mock_state_file (Path): a mocked state file in the test directory.
        experiment_tracker_state_component (MatchaStateComponent): the component used for finding a property
    """
    invalid_property_name = "invalid"
    with pytest.raises(MatchaError) as err:
        _ = experiment_tracker_state_component.find_property(
            property_name=invalid_property_name
        )

    assert (
        str(err.value)
        == f"The property with the name '{invalid_property_name}' could not be found."
    )


def test_matcha_state_build_state_from_terraform_output(
    state_file_as_object: MatchaState,
):
    """Test that a MatchaState object with the correct format is returned from the build_state_from_terraform_output function.

    Args:
        state_file_as_object (MatchaState): the state as a MatchaState object.
    """
    os.makedirs(".matcha/infrastructure", exist_ok=True)
    terraform_client_output = {
        "cloud_azure_resource_group_name": {
            "value": "test_resources",
        },
        "container_registry_azure_registry_name": {
            "value": "azure_registry_name",
        },
        "container_registry_azure_registry_url": {
            "value": "azure_container_registry",
        },
        "experiment_tracker_mlflow_tracking_url": {
            "value": "mlflow_test_url",
        },
    }
    matcha_state_service = MatchaStateService(terraform_output=terraform_client_output)

    assert isinstance(matcha_state_service._state, MatchaState)
    assert matcha_state_service._state == state_file_as_object
