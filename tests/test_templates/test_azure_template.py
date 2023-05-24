"""Test suite to test the azure template."""
import os
from unittest.mock import patch

import pytest

from matcha_ml.templates.azure_template.azure_template import AzureTemplate


@pytest.fixture
def azure_template() -> AzureTemplate:
    """Azure template object for testing.

    Returns:
        AzureTemplate: the Azure template.
    """
    return AzureTemplate()


def test_reuse_configuration(
    matcha_testing_directory: str, azure_template: AzureTemplate
):
    """Test the reuse_configuration function of AzureTemplate.

    Args:
        matcha_testing_directory (str): The path to the testing directory.
        azure_template (AzureTemplate): An instance of AzureTemplate.
    """
    test_config_dir = os.path.join(matcha_testing_directory, "test_config")
    assert not azure_template.reuse_configuration(test_config_dir)

    os.makedirs(test_config_dir)

    matcha_state_service_stub = (
        "matcha_ml.templates.azure_template.azure_template.MatchaStateService"
    )

    with patch(
        "matcha_ml.templates.azure_template.azure_template.check_current_deployment_exists"
    ) as mock_check_current_deployment_exists, patch(
        "typer.confirm"
    ) as mock_confirm, patch(
        matcha_state_service_stub
    ) as mock_matcha_state_service, patch(
        f"{matcha_state_service_stub}.fetch_resources_from_state_file"
    ) as mock_fetch_resources_from_state_file:

        mock_check_current_deployment_exists.return_value = True
        mock_confirm.return_value = True
        mock_matcha_state_service_instance = mock_matcha_state_service.return_value
        mock_matcha_state_service_instance.return_value = None
        mock_fetch_resources_from_state_file.return_value = None

        assert not azure_template.reuse_configuration(test_config_dir)

        mock_confirm.return_value = False

        assert azure_template.reuse_configuration(test_config_dir)
