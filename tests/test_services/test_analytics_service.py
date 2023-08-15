"""Tests for analytics service."""
import os
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from matcha_ml.cli.cli import app
from matcha_ml.errors import MatchaError
from matcha_ml.services.analytics_service import (
    AnalyticsEvent,
    _execute_analytics_event,
    _get_state_uuid,
    _post_event,
    _time_event,
)
from matcha_ml.services.global_parameters_service import GlobalParameters

CORE_FUNCTION_STUB = "matcha_ml.core.core"
ANALYTICS_SERVICE_FUNCTION_STUB = "matcha_ml.services.analytics_service"
GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB = (
    "matcha_ml.services.analytics_service.GlobalParameters"
)
MATCHA_STATE_SERVICE_FUNCTION_STUB = (
    "matcha_ml.services.analytics_service.MatchaStateService"
)


@pytest.fixture(autouse=True)
def mocked_global_parameters_service(matcha_testing_directory, uuid_for_testing):
    """Mocked global parameters service.

    Args:
        matcha_testing_directory (str): Temporary directory for testing.
        uuid_for_testing (uuid.UUID): a UUID which acts as a mock for the user_id

    Yields:
        GlobalParameters: GlobalParameters object with mocked properties.
    """
    with patch(
        f"{GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB}.default_config_file_path",
        new_callable=PropertyMock,
    ) as file_path, patch(
        f"{GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB}.user_id",
        new_callable=PropertyMock,
    ) as user_id:
        file_path.return_value = str(
            os.path.join(str(matcha_testing_directory), ".matcha-ml", "config.yaml")
        )
        user_id.return_value = str(uuid_for_testing)

        yield GlobalParameters()


@pytest.fixture
def mocked_matcha_state_service():
    """A fixture returning a mocked MatchaStateService instance.

    Yields:
        (MatchaStateService): a mocked MatchaStateService instance.
    """
    with patch(MATCHA_STATE_SERVICE_FUNCTION_STUB) as mocked_matcha_state_service_class:
        yield mocked_matcha_state_service_class()


def test_get_state_uuid_with_state(uuid_for_testing):
    """Test the _get_state_uuid private function where state exists.

    Args:
        uuid_for_testing (uuid.UUID): a fixed valid UUID4 value.
    """
    with patch(MATCHA_STATE_SERVICE_FUNCTION_STUB) as mock_matcha_state_service:
        mock_matcha_state_service.return_value.state_exists.return_value = True
        mock_component = (
            mock_matcha_state_service.return_value.get_component.return_value
        )
        mock_component.find_property.return_value.value = uuid_for_testing
        result = _get_state_uuid()

    assert result.value == uuid_for_testing


def test_get_state_uuid_without_state(mocked_matcha_state_service):
    """Test the _get_state_uuid private function where no state exists.

    Args:
        mocked_matcha_state_service (MatchaStateService): a mocked MatchaStateService instance.
    """
    mocked_matcha_state_service.side_effect = MatchaError("test")

    with pytest.raises(MatchaError):
        _ = _get_state_uuid()


@patch(MATCHA_STATE_SERVICE_FUNCTION_STUB)
def test_get_state_uuid_without_id_component(mocked_matcha_state_service):
    """Test the _get_state_uuid private function where state lacks an ID component.

    Args:
        mocked_matcha_state_service (MatchaStateService): a mocked MatchaStateService instance.
    """
    mocked_matcha_state_service = PropertyMock
    mocked_matcha_state_service.side_effect = MatchaError("test")

    with pytest.raises(MatchaError):
        _ = _get_state_uuid()


def test_execute_analytics_event():
    """Test the _execute_analytics_event private function."""
    test_function = MagicMock()
    test_function.return_value = 42
    result = _execute_analytics_event(test_function)

    test_function.assert_called_once()
    assert result == (42, None)


def test_execute_analytics_event_error_handling():
    """Test the _execute_analytics_event private function error handling."""

    def mock_function(*args, **kwargs):
        raise Exception("Mocked exception")

    test_function = mock_function

    result, error_code = _execute_analytics_event(test_function)

    assert result is None
    assert isinstance(error_code, Exception)
    assert str(error_code) == "Mocked exception"


def test_time_event():
    """Test the _time_event private function."""
    with patch(
        f"{ANALYTICS_SERVICE_FUNCTION_STUB}._execute_analytics_event"
    ) as execute_analytics_event:
        execute_analytics_event.return_value = ("test_output", None)

        result, error_code, ts, te = _time_event(MagicMock())

    execute_analytics_event.assert_called()
    assert result == "test_output"
    assert error_code is None
    assert te > ts


def test_post_event(mocked_global_parameters_service):
    """Test the _post_event private function.

    Args:
        mocked_global_parameters_service (GlobalParametersService): a mocked global parameters service for testing.
    """
    mocked_global_parameters_service_instance = mocked_global_parameters_service
    with patch(
        f"{ANALYTICS_SERVICE_FUNCTION_STUB}.analytics.Client.track"
    ) as mock_client:
        _ = _post_event(
            event_name=AnalyticsEvent.PROVISION,
            matcha_state_uuid=None,
            global_params=mocked_global_parameters_service_instance,
            error_code=None,
            time_taken=1.0,
        )
        mock_client.assert_called


def test_segment_track_receives_the_correct_arguments(
    runner,
    matcha_testing_directory,
    mocked_segment_track_decorator,
    uuid_for_testing,
    mock_state_file,
):
    """Test the Segment track function receives the expected arguments when a user is opted in to analytics.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
        mocked_segment_track_decorator (MagicMock): mocked Segment track call found in 'matcha_ml.services.analytics_service.analytics.track'
        uuid_for_testing (uuid.UUID): a UUID which acts as a mock for the matcha_state_id
        mock_state_file (None): a mocked state file in the test directory.
    """
    os.chdir(matcha_testing_directory)

    with patch(f"{CORE_FUNCTION_STUB}.AzureRunner") as azure_runner, patch(
        f"{CORE_FUNCTION_STUB}.RemoteStateManager"
    ) as remote_state_manager:
        azure_runner.return_value = MagicMock()
        remote_state_manager.return_value = MagicMock()

        runner.invoke(app, ["destroy"], input="Y\n")

        # Check that the mocked segment track was called
        mocked_segment_track_decorator.assert_called()

        tracked_arguments = mocked_segment_track_decorator.call_args.args
        # Check that the Segment track arguments are as expected
        assert str(uuid_for_testing) in tracked_arguments
        assert "destroy" in tracked_arguments
        assert {
            "time_taken",
            "error_type",
            "command_succeeded",
            "matcha_state_uuid",
        } == set(tracked_arguments[2].keys())


def test_tracking_does_not_happen_when_opted_out(
    runner, matcha_testing_directory, mocked_segment_track_decorator
):
    """Test Segment track is not called when the user is opted out of data analytics collection.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
        mocked_segment_track_decorator (MagicMock): mocked Segment track call found in 'matcha_ml.services.analytics_service.analytics.track'
    """
    os.chdir(matcha_testing_directory)

    # Invoke destroy command with a GlobalParameter opting out of data collection
    with patch(
        f"{GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB}.analytics_opt_out",
        new_callable=PropertyMock,
    ):
        runner.invoke(app, ["destroy"])

    # Check that the mocked segment track was not called
    mocked_segment_track_decorator.assert_not_called()
