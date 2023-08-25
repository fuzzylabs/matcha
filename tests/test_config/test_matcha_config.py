"""Tests for Matcha Config module."""

import json
import os
from typing import Dict, Iterator

import pytest

from matcha_ml.config.matcha_config import (
    DEFAULT_CONFIG_NAME,
    MatchaConfig,
    MatchaConfigComponent,
    MatchaConfigComponentProperty,
    MatchaConfigService,
)
from matcha_ml.errors import MatchaError


def test_matcha_config_to_dict(
    mocked_matcha_config_json_object: Dict[str, Dict[str, str]],
    mocked_matcha_config: MatchaConfig,
):
    """Tests the to_dict method of the MatchaConfig class.

    The test compares the output of the MatchaConfig to_dict method with a dictionary representation of the matcha.config.json file.

    Args:
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file
        mocked_matcha_config (MatchaConfig): a mocked MatchaConfig instance.
    """
    assert mocked_matcha_config_json_object == mocked_matcha_config.to_dict()


def test_matcha_config_from_dict(
    mocked_matcha_config_json_object: Dict[str, Dict[str, str]],
    mocked_matcha_config: MatchaConfig,
):
    """Tests the from_dict method of the MatchaConfig class.

    The test compares the output of the MatchaConfig from_dict method with a mocked MatchaConfig instance.

    Args:
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file
        mocked_matcha_config (MatchaConfig): a mocked MatchaConfig instance.
    """
    assert (
        mocked_matcha_config.from_dict(mocked_matcha_config_json_object)
        == mocked_matcha_config
    )


def test_matcha_config_service_write_matcha_config(
    matcha_testing_directory: Iterator[str],
    mocked_matcha_config_service: MatchaConfigService,
    mocked_matcha_config: MatchaConfig,
):
    """Tests the write_matcha_config method of the MatchaConfigService.

    The test creates a testing directory and a mock matcha.config.json file to test the read_matcha_config method.

    Args:
        matcha_testing_directory (Iterator[str]): a fixture for creating and removing temporary test directory for storing and moving files
        mocked_matcha_config_service (MatchaConfigService): a mocked MatchaConfigService instance
        mocked_matcha_config (MatchaConfig): a mocked MatchaConfig instance
    """
    matcha_config_file_path = os.path.join(
        matcha_testing_directory, DEFAULT_CONFIG_NAME
    )

    assert not os.path.isfile(matcha_config_file_path)

    os.chdir(matcha_testing_directory)

    mocked_matcha_config_service.write_matcha_config(mocked_matcha_config)

    assert mocked_matcha_config_service.read_matcha_config() == mocked_matcha_config


def test_matcha_config_service_read_matcha_config(
    matcha_testing_directory: Iterator[str],
    mocked_matcha_config_service: MatchaConfigService,
    mocked_matcha_config: MatchaConfig,
    mocked_matcha_config_json_object: Dict[str, Dict[str, str]],
):
    """Tests the read_matcha_config method of the MatchaConfigService.

    The test creates a testing directory and a mock matcha.config.json file to test the read_matcha_config method.

    Args:
        matcha_testing_directory (Iterator[str]): a fixture for creating and removing temporary test directory for storing and moving files
        mocked_matcha_config_service (MatchaConfigService): a mocked MatchaConfigService instance
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file
        mocked_matcha_config (MatchaConfig): a mocked MatchaConfig instance
    """
    matcha_config_file_path = os.path.join(
        matcha_testing_directory, DEFAULT_CONFIG_NAME
    )

    with open(matcha_config_file_path, "w") as file:
        json.dump(mocked_matcha_config_json_object, file)

    os.chdir(matcha_testing_directory)

    assert mocked_matcha_config_service.read_matcha_config() == mocked_matcha_config


def test_matcha_config_service_read_matcha_config_with_no_config(
    matcha_testing_directory: Iterator[str],
):
    """Tests the error handling of the read_matcha_config method of the MatchaConfigService.

    This test expects a MatchaError to be thrown if the config rile cannot be read.

    Args:
        matcha_testing_directory (Iterator[str]): a fixture for creating and removing temporary test directory for storing and moving files
    """
    os.chdir(matcha_testing_directory)

    with pytest.raises(MatchaError):
        _ = MatchaConfigService.read_matcha_config()


def test_matcha_config_service_delete_matcha_config(
    matcha_testing_directory: Iterator[str],
    mocked_matcha_config_service: MatchaConfigService,
    mocked_matcha_config_json_object: Dict[str, Dict[str, str]],
):
    """Tests the delete_matcha_config method of the MatchaConfigService.

    The test creates a testing directory and a mock matcha.config.json file to then destroy, testing the delete_matcha_config method.

    Args:
        matcha_testing_directory (Iterator[str]): a fixture for creating and removing temporary test directory for storing and moving files
        mocked_matcha_config_service (MatchaConfigService): a mocked MatchaConfigService instance
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file
    """
    matcha_config_file_path = os.path.join(
        matcha_testing_directory, DEFAULT_CONFIG_NAME
    )

    with open(matcha_config_file_path, "w") as file:
        json.dump(mocked_matcha_config_json_object, file)

    assert os.path.isfile(matcha_config_file_path)

    os.chdir(matcha_testing_directory)

    mocked_matcha_config_service.delete_matcha_config()

    assert not os.path.isfile(matcha_config_file_path)


def test_matcha_config_service_delete_matcha_config_error_handling(
    matcha_testing_directory: Iterator[str],
    mocked_matcha_config_service: MatchaConfigService,
):
    """Tests the error handling of the delete_matcha_config method of the MatchaConfigService.

    The test asserts that no file exist and then attempts to destroy the non-existent file.

    Args:
        matcha_testing_directory (Iterator[str]): a fixture for creating and removing temporary test directory for storing and moving files
        mocked_matcha_config_service (MatchaConfigService): a mocked MatchaConfigService instance
    """
    matcha_config_file_path = os.path.join(
        matcha_testing_directory, DEFAULT_CONFIG_NAME
    )

    assert not os.path.isfile(matcha_config_file_path)

    os.chdir(matcha_testing_directory)

    with pytest.raises(MatchaError):
        mocked_matcha_config_service.delete_matcha_config()


def test_find_component_expected(
    mocked_matcha_config: MatchaConfig,
):
    """Test that a component is found when a valid component name is given.

    Args:
        mocked_matcha_config (MatchaConfig): a mocked MatchaConfig instance.
    """
    component = mocked_matcha_config.find_component(
        component_name="remote_state_bucket"
    )

    assert component.find_property("account_name").value == "test-account"
    assert component.find_property("container_name").value == "test-container"
    assert component.find_property("resource_group_name").value == "test-rg"


def test_find_component_not_found(
    mocked_matcha_config: MatchaConfig,
):
    """Test that a component is not found when an invalid component name is given.

    Args:
        mocked_matcha_config (MatchaConfig): a mocked MatchaConfig instance.
    """
    component = mocked_matcha_config.find_component(
        component_name="invalid_resource_name"
    )

    assert component is None


def test_matcha_config_service_update(
    matcha_testing_directory, mocked_matcha_config_json_object
) -> None:
    """Test that the update function in MatchaConfigService creates the desired changes in config file.

    Args:
        matcha_testing_directory (str): A temporary working directory.
        mocked_matcha_config_json_object (dict): A dictionary representation of a matcha config json file.
    """
    os.chdir(matcha_testing_directory)
    config = MatchaConfig.from_dict(mocked_matcha_config_json_object)
    config_dict = config.to_dict()

    MatchaConfigService.write_matcha_config(config)

    component = MatchaConfigComponent(
        name="test",
        properties=[MatchaConfigComponentProperty(name="name", value="passed")],
    )

    MatchaConfigService.update(component)

    updated_config = MatchaConfigService.read_matcha_config()
    updated_config_dict = updated_config.to_dict()

    assert len(updated_config_dict) - 1 == len(config_dict)
    assert config_dict.items() <= updated_config_dict.items()
    assert updated_config_dict["test"]["name"] == "passed"

    MatchaConfigService.delete_matcha_config()
    MatchaConfigService.write_matcha_config(config)

    components = [
        MatchaConfigComponent(
            name="test",
            properties=[MatchaConfigComponentProperty(name="name", value="passed")],
        ),
        MatchaConfigComponent(
            name="test2",
            properties=[
                MatchaConfigComponentProperty(name="name", value="passed_again")
            ],
        ),
    ]

    MatchaConfigService.update(components)

    updated_config = MatchaConfigService.read_matcha_config()
    updated_config_dict = updated_config.to_dict()

    assert len(updated_config_dict) - 2 == len(config_dict)
    assert config_dict.items() <= updated_config_dict.items()
    assert updated_config_dict["test"]["name"] == "passed"
    assert updated_config_dict["test2"]["name"] == "passed_again"


def test_remove_property_expected(
    mocked_matcha_config_component: MatchaConfigComponent,
):
    """Test that a component is removed if it exists.

    Args:
        mocked_matcha_config_component (MatchaConfigComponent): a mocked MatchaConfigComponent instance.
    """
    mocked_matcha_config_component.remove_property(property_name="account_name")
    mocked_matcha_config_component.remove_property(property_name="resource_group_name")
    mocked_matcha_config_component.remove_property(
        property_name="not_an_existing_property_name"
    )

    assert mocked_matcha_config_component == MatchaConfigComponent(
        name="remote_state_bucket",
        properties=[
            MatchaConfigComponentProperty(name="container_name", value="test-container")
        ],
    )


def test_add_property_expected(
    matcha_testing_directory, mocked_matcha_config_json_object
):
    """Test adding a property.

    Args:
        matcha_testing_directory (str): A temporary working directory.
        mocked_matcha_config_json_object (dict): A dictionary representation of a matcha config json file.
    """
    os.chdir(matcha_testing_directory)
    config = MatchaConfig.from_dict(mocked_matcha_config_json_object)
    config_dict = config.to_dict()

    MatchaConfigService.write_matcha_config(config)

    component_property = MatchaConfigComponentProperty(name="name", value="passed")
    second_component_property = MatchaConfigComponentProperty(
        name="location", value="ukwest"
    )

    MatchaConfigService.add_property(
        component_name="test", component_property=component_property
    )
    MatchaConfigService.add_property(
        component_name="test", component_property=second_component_property
    )

    updated_config = MatchaConfigService.read_matcha_config()
    updated_config_dict = updated_config.to_dict()

    assert len(updated_config_dict) - 1 == len(config_dict)
    assert config_dict.items() <= updated_config_dict.items()
    assert updated_config_dict["test"]["name"] == "passed"
    assert updated_config_dict["test"]["location"] == "ukwest"


def test_remove_property_config_service_expected(
    matcha_testing_directory, mocked_matcha_config_json_object
):
    """Test removing a property from the ConfigService level.

    Args:
        matcha_testing_directory (str): A temporary working directory.
        mocked_matcha_config_json_object (dict): A dictionary representation of a matcha config json file.
    """
    os.chdir(matcha_testing_directory)
    config = MatchaConfig.from_dict(mocked_matcha_config_json_object)

    MatchaConfigService.write_matcha_config(config)

    config_dict = MatchaConfigService.read_matcha_config().to_dict()
    assert config_dict["remote_state_bucket"]["account_name"] == "test-account"

    MatchaConfigService.remove_property(
        component_name="remote_state_bucket", property_name="account_name"
    )

    updated_config = MatchaConfigService.read_matcha_config()
    updated_config_dict = updated_config.to_dict()

    assert updated_config_dict.get("remote_state_bucket").get("account_name") is None
