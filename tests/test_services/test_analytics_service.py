"""Tests for analytics service."""
import os
from unittest.mock import PropertyMock, patch

import pytest

from matcha_ml.cli.cli import app
from matcha_ml.services.global_parameters_service import GlobalParameters

GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB = (
    "matcha_ml.services.analytics_service.GlobalParameters"
)


@pytest.fixture(autouse=True)
def mocked_global_parameters_service(matcha_testing_directory):
    """Mocked global parameters service.

    Args:
        matcha_testing_directory (str): Temporary directory for testing.

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
        user_id.return_value = "TestUserID"

        yield GlobalParameters()


def test_segment_track_recieves_the_correct_arguments(
    runner, matcha_testing_directory, mocked_segment_track_decorator
):
    """Test no the Segment track function recieves the expected arguments when a user is opted in to analytics.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
        mocked_segment_track_decorator (MagicMock): mocked Segment track call found in 'matcha_ml.services.analytics_service.analytics.track'
    """
    os.chdir(matcha_testing_directory)

    # Invoke destroy command
    with patch(
        "matcha_ml.templates.azure_template.check_current_deployment_exists"
    ) as check_deployment_exists:
        check_deployment_exists.return_value = False
        runner.invoke(app, ["destroy"])

    # Check that the mocked segment track was called
    mocked_segment_track_decorator.assert_called()

    tracked_arguments = mocked_segment_track_decorator.call_args.args
    # Check that the Segment track arguments are as expected
    assert "TestUserID" in tracked_arguments
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
        "matcha_ml.templates.azure_template.check_current_deployment_exists"
    ) as check_deployment_exists, patch(
        f"{GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB}.analytics_opt_out",
        new_callable=PropertyMock,
    ):
        check_deployment_exists.return_value = False
        runner.invoke(app, ["destroy"])

    # Check that the mocked segment track was not called
    mocked_segment_track_decorator.assert_not_called()
