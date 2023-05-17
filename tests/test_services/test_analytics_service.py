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


def test_cli_destroy_command_analytics_are_mocked(
    runner, matcha_testing_directory, mocked_segment_track_decorator
):
    """Test no external api calls are sent with Segment.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
        mocked_segment_track_decorator (MagicMock): mocked Segment track call found in 'matcha_ml.services.analytics_service.analytics.track'
    """
    os.chdir(matcha_testing_directory)

    # Invoke destroy command
    with patch(
        "matcha_ml.templates.build_templates.azure_template.check_current_deployment_exists"
    ) as check_deployment_exists:
        check_deployment_exists.return_value = False
        result = runner.invoke(app, ["destroy"])

    assert (
        "Error - you cannot destroy resources that have not been provisioned yet."
        in result.stdout
    )

    # Check that the mocked segment track was called
    mocked_segment_track_decorator.assert_called()
