"""Tests for Matcha Config module."""

import json
import os

import pytest

from matcha_ml.config.matcha_config import (
    MatchaConfig,
    MatchaConfigComponent,
    MatchaConfigComponentProperty,
    MatchaConfigService,
)


@pytest.fixture
def mocked_matcha_config_json_object():
    """docstring."""
    matcha_config = {
        "remote_state_bucket": {
            "account_name": "test_account_name",
            "container_name": "test_container_name",
            "resource_group_name": "test_resource_group_name",
        }
    }

    return matcha_config


@pytest.fixture
def mocked_matcha_config_component_property():
    """docstring."""
    return MatchaConfigComponentProperty(name="account_name", value="test_account_name")


@pytest.fixture
def mocked_matcha_config_component(mocked_matcha_config_json_object):
    """docstring."""
    properties = []
    for key, value in mocked_matcha_config_json_object["remote_state_bucket"].items():
        properties.append(MatchaConfigComponentProperty(name=key, value=value))

    return MatchaConfigComponent(name="remote_state_bucket", properties=properties)


@pytest.fixture
def mocked_matcha_config(mocked_matcha_config_component):
    """docstring."""
    return MatchaConfig([mocked_matcha_config_component])


@pytest.fixture
def mocked_matcha_config_service():
    """docstring."""
    return MatchaConfigService()


def test_matcha_config_to_dict(mocked_matcha_config_json_object, mocked_matcha_config):
    """docstring."""
    assert mocked_matcha_config_json_object == mocked_matcha_config.to_dict()


def test_matcha_config_from_dict(
    mocked_matcha_config_json_object, mocked_matcha_config
):
    """docstring."""
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
    """docstring."""
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
    """docstring."""
    matcha_config_file_path = os.path.join(
        matcha_testing_directory, "matcha.config.json"
    )

    with open(matcha_config_file_path, "w") as file:
        json.dump(mocked_matcha_config_json_object, file)

    assert os.path.isfile(matcha_config_file_path)

    os.chdir(matcha_testing_directory)

    mocked_matcha_config_service.delete_matcha_config()

    assert not os.path.isfile(matcha_config_file_path)
