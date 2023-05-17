"""Reusable fixtures for test_cli."""
import os
from unittest.mock import PropertyMock, patch

import pytest

from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.templates.run_template import TemplateRunner

INTERNAL_FUNCTION_STUB = "matcha_ml.cli.provision.TemplateRunner"

GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB = (
    "matcha_ml.services.analytics_service.GlobalParameters"
)


@pytest.fixture(scope="class", autouse=True)
def mocked_template_runner() -> TemplateRunner:
    """The Template Runner with mocked variables.

    Returns:
        TemplateRunner: the mocked TemplateRunner.
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}._initialize_terraform") as initialize, patch(
        f"{INTERNAL_FUNCTION_STUB}._apply_terraform"
    ) as apply, patch(
        f"{INTERNAL_FUNCTION_STUB}._show_terraform_outputs"
    ) as show, patch(
        f"{INTERNAL_FUNCTION_STUB}._check_terraform_installation"
    ) as check_tf_install, patch(
        f"{INTERNAL_FUNCTION_STUB}._validate_terraform_config"
    ) as validate_tf_config:
        initialize.return_value = None
        apply.return_value = None
        show.return_value = None
        check_tf_install.return_value = None
        validate_tf_config.return_value = None

        yield TemplateRunner()


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

        yield GlobalParameters
