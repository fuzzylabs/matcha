"""Tests for Global Config Service."""
import os
from unittest import mock

import pytest
import yaml

from matcha_ml.services.global_config_service import GlobalConfigurationService

INTERNAL_FUNCTION_STUB = (
    "matcha_ml.services.global_config_service.GlobalConfigurationService"
)


@pytest.fixture(autouse=True)
def teardown_singleton():
    """Tears down the singleton before each test case by clearing the current object."""
    GlobalConfigurationService.clear()


def test_class_is_singleton(matcha_testing_directory):
    """Tests that the GlobalConfigurationService is correctly implemented as a singleton.

    Args:
        matcha_testing_directory (str): Mock testing directory location for the GlobalConfig file to be located
    """
    with mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.default_config_file_path",
        new_callable=mock.PropertyMock,
    ) as file_path:
        file_path.return_value = str(
            os.path.join(str(matcha_testing_directory), ".matcha-ml", "config.yaml")
        )

        first_instance = GlobalConfigurationService()
        second_instance = GlobalConfigurationService()
        assert first_instance is second_instance

        first_instance._instance = None


def test_new_config_file_creation(matcha_testing_directory):
    """Tests that a new file is created if it does not exist when the global config object is instantiated.

    Args:
        matcha_testing_directory (str): Mock testing directory location for the GlobalConfig file to be located
    """
    config_file_path = os.path.join(
        matcha_testing_directory, ".matcha-ml", "config.yaml"
    )
    with mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.default_config_file_path",
        new_callable=mock.PropertyMock,
    ) as file_path:
        file_path.return_value = config_file_path

        assert not os.path.exists(config_file_path)
        GlobalConfigurationService()
        assert os.path.exists(config_file_path)


def test_existing_config_file(matcha_testing_directory):
    """Tests that the class variables are updated when there is an existing global config file.

    Args:
        matcha_testing_directory (str): Mock testing directory location for the GlobalConfig file to be located
    """
    config_file_path = os.path.join(
        matcha_testing_directory, ".matcha-ml", "config.yaml"
    )

    data = {
        "user_id": "TestID",
        "analytics_opt_out": False,
    }

    # Create the '.matcha-ml' config directory
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
    # Create config file and populate with the current class variables
    with open(config_file_path, "w") as file:
        yaml.dump(data, file)

    with mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.default_config_file_path",
        new_callable=mock.PropertyMock,
    ) as file_path:
        file_path.return_value = config_file_path

        config_instance = GlobalConfigurationService()
        assert config_instance.config_file == {
            "user_id": "TestID",
            "analytics_opt_out": False,
        }
        assert config_instance.user_id == "TestID"
        assert config_instance.analytics_opt_out is False


def test_opt_out(matcha_testing_directory):
    """Tests that the opt out function changes the class variables and the global config file.

    Args:
        matcha_testing_directory (str): Mock testing directory location for the GlobalConfig file to be located
    """
    config_file_path = os.path.join(
        matcha_testing_directory, ".matcha-ml", "config.yaml"
    )

    with mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.default_config_file_path",
        new_callable=mock.PropertyMock,
    ) as file_path:
        file_path.return_value = config_file_path

        config_instance = GlobalConfigurationService()

        assert config_instance.config_file.get("analytics_opt_out") is False
        assert config_instance.analytics_opt_out is False

        config_instance.opt_out_of_analytics()

        assert config_instance.config_file.get("analytics_opt_out") is True
        assert config_instance.analytics_opt_out is True
