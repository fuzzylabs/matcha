"""Reusable fixtures for test_cli."""
import os
from unittest.mock import PropertyMock, patch

import pytest

from matcha_ml.runners import AzureRunner, RemoteStateRunner
from matcha_ml.services.global_parameters_service import GlobalParameters

INTERNAL_FUNCTION_STUBS = [
    "matcha_ml.cli.provision.AzureRunner",
    "matcha_ml.state.remote_state_manager.RemoteStateRunner",
]

GLOBAL_PARAMETER_SERVICE_FUNCTION_STUB = (
    "matcha_ml.services.analytics_service.GlobalParameters"
)


@pytest.fixture(scope="class", autouse=True)
def mocked_resource_template_runner() -> AzureRunner:
    """The Template Runner with mocked variables.

    Returns:
        AzureRunner: the mocked TemplateRunner.
    """
    with patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._initialize_terraform"
    ) as initialize, patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._apply_terraform"
    ) as apply, patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._show_terraform_outputs"
    ) as show, patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._check_terraform_installation"
    ) as check_tf_install, patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._validate_terraform_config"
    ) as validate_tf_config:
        initialize.return_value = None
        apply.return_value = None
        show.return_value = None
        check_tf_install.return_value = None
        validate_tf_config.return_value = None

        yield AzureRunner()


@pytest.fixture(scope="class", autouse=True)
def mocked_state_storage_template_runner() -> RemoteStateRunner:
    """The Template Runner with mocked variables.

    Returns:
        RemoteStateRunner: the mocked TemplateRunner.
    """
    with patch(
        f"{INTERNAL_FUNCTION_STUBS[1]}._initialize_terraform"
    ) as initialize, patch(
        f"{INTERNAL_FUNCTION_STUBS[1]}._apply_terraform"
    ) as apply, patch(
        f"{INTERNAL_FUNCTION_STUBS[1]}._check_terraform_installation"
    ) as check_tf_install, patch(
        f"{INTERNAL_FUNCTION_STUBS[1]}._validate_terraform_config"
    ) as validate_tf_config, patch(
        f"{INTERNAL_FUNCTION_STUBS[1]}._get_terraform_output"
    ) as get:
        initialize.return_value = None
        apply.return_value = None
        check_tf_install.return_value = None
        validate_tf_config.return_value = None
        get.return_value = (
            "test-account",
            "test-container",
            "test-rg",
        )

        yield RemoteStateRunner()


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
