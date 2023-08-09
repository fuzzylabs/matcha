"""Test suite to test the stack set functionality in matcha."""
import os
from unittest.mock import patch

import pytest

from matcha_ml.config import MatchaConfig, MatchaConfigService
from matcha_ml.core import stack_set
from matcha_ml.errors import MatchaInputError


def test_stack_set_valid_no_existing_file(matcha_testing_directory):
    """Test that stack_set creates a config file if one doesn't exist and that it can be read properly.

    Args:
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    with patch(
        "matcha_ml.state.remote_state_manager.RemoteStateManager.is_state_provisioned"
    ) as is_state_provisioned:
        is_state_provisioned.return_value = False
        stack_set(stack_name="llm")

    config = MatchaConfigService.read_matcha_config()
    assert config.to_dict() == {"stack": {"name": "LLM"}}

    MatchaConfigService.delete_matcha_config()

    with patch(
        "matcha_ml.state.remote_state_manager.RemoteStateManager.is_state_provisioned"
    ) as is_state_provisioned:
        is_state_provisioned.return_value = False
        stack_set(stack_name="default")

    config = MatchaConfigService.read_matcha_config()
    assert config.to_dict() == {"stack": {"name": "DEFAULT"}}


def test_stack_set_invalid(matcha_testing_directory):
    """Test stack_set raises an error if an invalid name is passed.

    Args:
        matcha_testing_directory (str): temporary working directory
    """
    with pytest.raises(MatchaInputError), patch(
        "matcha_ml.state.remote_state_manager.RemoteStateManager.is_state_provisioned"
    ) as is_state_provisioned:
        is_state_provisioned.return_value = False
        stack_set("nonsense")


def test_stack_set_existing_file(
    mocked_matcha_config_json_object, matcha_testing_directory
):
    """Test that if there's an existing file, the stack set command does not remove existing configuration information.

    Args:
        mocked_matcha_config_json_object (dict): a dictionary representation of the matcha.config.json file
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    config = MatchaConfig.from_dict(mocked_matcha_config_json_object)
    config_dict = config.to_dict()
    MatchaConfigService.write_matcha_config(config)

    with patch(
        "matcha_ml.state.remote_state_manager.RemoteStateManager.is_state_provisioned"
    ) as is_state_provisioned:
        is_state_provisioned.return_value = False
        stack_set("llm")

    new_config = MatchaConfigService.read_matcha_config()
    new_config_dict = new_config.to_dict()

    assert len(new_config_dict) == len(config_dict) + 1
    assert "stack" in new_config_dict
    assert new_config_dict["stack"]["name"] == "LLM"
    assert config_dict.items() <= new_config_dict.items()
