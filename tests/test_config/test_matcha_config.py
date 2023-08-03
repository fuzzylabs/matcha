"""Tests for Matcha Config module."""

import json
import os
from typing import Dict

import pytest

from matcha_ml.config.matcha_config import (
    MatchaConfig,
    MatchaConfigComponent,
    MatchaConfigComponentProperty,
    MatchaConfigService,
)


@pytest.fixture
def mocked_matcha_config_json_object() -> Dict[str, Dict[str, str]]:
    """A fixture returning a dictionary representation of the matcha.config.json file.

    Returns:
        matcha_config (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file
    """
    matcha_config = {
        "remote_state_bucket": {
            "account_name": "test_account_name",
            "container_name": "test_container_name",
            "resource_group_name": "test_resource_group_name",
        }
    }

    return matcha_config


@pytest.fixture
def mocked_matcha_config_component_property() -> MatchaConfigComponentProperty:
    """A fixture returning a mocked MatchaConfigComponentProperty instance.

    Returns:
        (MatchaConfigComponentProperty): a mocked MatchaConfigComponentProperty instance.
    """
    return MatchaConfigComponentProperty(name="account_name", value="test_account_name")


@pytest.fixture
def mocked_matcha_config_component(mocked_matcha_config_json_object):
    """A fixture returning a mocked MatchaConfigComponentProperty instance.

    Args:
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file

    Returns:
        (MatchaConfigComponentProperty): a mocked MatchaConfigComponentProperty instance.
    """
    properties = []
    for key, value in mocked_matcha_config_json_object["remote_state_bucket"].items():
        properties.append(MatchaConfigComponentProperty(name=key, value=value))

    return MatchaConfigComponent(name="remote_state_bucket", properties=properties)


@pytest.fixture
def mocked_matcha_config(mocked_matcha_config_component):
    """A fixture returning a mocked MatchaConfig instance.

    Args:
        mocked_matcha_config_component (MatchaConfigComponent): a mocked MatchaConfigComponent instance.

    Returns:
        (MatchaConfig): a mocked MatchaConfig instance.
    """
    return MatchaConfig([mocked_matcha_config_component])


@pytest.fixture
def mocked_matcha_config_service():
    """A fixture representing a mocked MatchaConfigService.

    Returns:
    (MatchaConfigService): a mocked MatchaConfigService instance.
    """
    return MatchaConfigService()


def test_matcha_config_to_dict(mocked_matcha_config_json_object, mocked_matcha_config):
    """Tests the to_dict method of the MatchaConfig class.

    The test compares the output of the MatchaConfig to_dict method with a dictionary representation of the matcha.config.json file.

    Args:
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file
        mocked_matcha_config (MatchaConfig): a mocked MatchaConfig instance.
    """
    assert mocked_matcha_config_json_object == mocked_matcha_config.to_dict()


def test_matcha_config_from_dict(
    mocked_matcha_config_json_object, mocked_matcha_config
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


def test_matcha_config_service_read_matcha_config(
    matcha_testing_directory,
    mocked_matcha_config_service,
    mocked_matcha_config,
    mocked_matcha_config_json_object,
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
        matcha_testing_directory, "matcha.config.json"
    )

    with open(matcha_config_file_path, "w") as file:
        json.dump(mocked_matcha_config_json_object, file)

    os.chdir(matcha_testing_directory)

    assert mocked_matcha_config_service.read_matcha_config() == mocked_matcha_config


def test_matcha_config_service_delete_matcha_config(
    matcha_testing_directory,
    mocked_matcha_config_service,
    mocked_matcha_config_json_object,
):
    """Tests the delete_matcha_config method of the MatchaConfigService.

    The test creates a testing directory and a mock matcha.config.json file to then destroy, testing the delete_matcha_config method.

    Args:
        matcha_testing_directory (Iterator[str]): a fixture for creating and removing temporary test directory for storing and moving files
        mocked_matcha_config_service (MatchaConfigService): a mocked MatchaConfigService instance
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file
    """
    matcha_config_file_path = os.path.join(
        matcha_testing_directory, "matcha.config.json"
    )

    with open(matcha_config_file_path, "w") as file:
        json.dump(mocked_matcha_config_json_object, file)

    assert os.path.isfile(matcha_config_file_path)

    os.chdir(matcha_testing_directory)

    mocked_matcha_config_service.delete_matcha_config()

    assert not os.path.isfile(matcha_config_file_path)
