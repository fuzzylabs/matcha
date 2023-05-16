"""Tests for analytics service."""
import os
from unittest.mock import patch

from matcha_ml.cli.cli import app


def test_cli_destroy_command_analytics_are_mocked(runner, matcha_testing_directory):
    """Test no external api calls are sent with Segment.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory.
    """
    os.chdir(matcha_testing_directory)

    # Invoke provision command
    with patch(
        "matcha_ml.templates.build_templates.azure_template.check_current_deployment_exists"
    ) as check_deployment_exists:
        check_deployment_exists.return_value = False
        result = runner.invoke(app, ["destroy"])

    assert (
        "Error - you cannot destroy resources that have not been provisioned yet."
        in result.stdout
    )
