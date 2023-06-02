"""Tests for Global Parameters Service."""
import os
from stat import S_IREAD
from unittest import mock

import pytest
import yaml

from matcha_ml.errors import MatchaPermissionError
from matcha_ml.services.global_parameters_service import GlobalParameters

INTERNAL_FUNCTION_STUB = "matcha_ml.services.global_parameters_service.GlobalParameters"


@pytest.fixture(autouse=True)
def teardown_singleton():
    """Tears down the singleton before each test case by clearing the current object."""
    GlobalParameters._instance = None


def test_class_is_singleton(matcha_testing_directory):
    """Tests that the GlobalParameters is correctly implemented as a singleton.

    Args:
        matcha_testing_directory (str): Mock testing directory location for the config file to be located
    """
    with mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.default_config_file_path",
        new_callable=mock.PropertyMock,
    ) as file_path:
        file_path.return_value = str(
            os.path.join(str(matcha_testing_directory), ".matcha-ml", "config.yaml")
        )

        first_instance = GlobalParameters()
        second_instance = GlobalParameters()
        assert first_instance is second_instance

        assert first_instance.user_id is second_instance.user_id
        assert first_instance.analytics_opt_out is second_instance.analytics_opt_out


def test_new_config_file_creation(matcha_testing_directory):
    """Tests that a new file is created if it does not exist when the global parameters object is instantiated.

    Args:
        matcha_testing_directory (str): Mock testing directory location for the config file to be located
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
        _ = GlobalParameters()
        assert os.path.exists(config_file_path)


def test_existing_config_file(matcha_testing_directory, uuid_for_testing):
    """Tests that the class variables are updated when there is an existing config file.

    Args:
        matcha_testing_directory (str): Mock testing directory location for the config file to be located
        uuid_for_testing (uuid.UUID): a UUID which acts as a mock for the user_id
    """
    config_file_path = os.path.join(
        matcha_testing_directory, ".matcha-ml", "config.yaml"
    )

    data = {
        "user_id": str(uuid_for_testing),
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

        config_instance = GlobalParameters()
        assert config_instance.config_file == {
            "user_id": str(uuid_for_testing),
            "analytics_opt_out": False,
        }
        assert config_instance.user_id == str(uuid_for_testing)
        assert config_instance.analytics_opt_out is False


def test_opt_out(matcha_testing_directory):
    """Tests that the opt out function changes the class variables and the global config file.

    Args:
        matcha_testing_directory (str): Mock testing directory location for the Global Parameteres file to be located
    """
    config_file_path = os.path.join(
        matcha_testing_directory, ".matcha-ml", "config.yaml"
    )

    with mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.default_config_file_path",
        new_callable=mock.PropertyMock,
    ) as file_path:
        file_path.return_value = config_file_path

        config_instance = GlobalParameters()

        assert config_instance.config_file.get("analytics_opt_out") is False
        assert config_instance.analytics_opt_out is False

        GlobalParameters().analytics_opt_out = True

        assert config_instance.config_file.get("analytics_opt_out") is True
        assert config_instance.analytics_opt_out is True


def test_config_file_write_permissions(matcha_testing_directory):
    """Tests the permissions error thrown where the user does not have permission to write a config file.

    Args:
        matcha_testing_directory (str): Mock testing directory location for the config file to be located
    """
    config_file_path = os.path.join(
        matcha_testing_directory, ".matcha-ml", "config.yaml"
    )
    with mock.patch(
        f"{INTERNAL_FUNCTION_STUB}.default_config_file_path",
        new_callable=mock.PropertyMock,
    ) as file_path:
        file_path.return_value = config_file_path

        # Alters the permissions on the testing directory to be read-only
        os.chmod(matcha_testing_directory, S_IREAD)

        with pytest.raises(MatchaPermissionError):
            _ = GlobalParameters()
