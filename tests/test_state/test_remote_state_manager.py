"""Test for the RemoteStateManager."""
import glob
import json
import os
from typing import Dict
from unittest.mock import patch

import pytest
from _pytest.capture import SysCapture

from matcha_ml.state.remote_state_manager import DEFAULT_CONFIG_NAME, RemoteStateManager
from matcha_ml.templates.build_templates.state_storage_template import SUBMODULE_NAMES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)


@pytest.fixture
def expected_matcha_config() -> Dict[str, Dict[str, str]]:
    """A fixture for the expected configuration for testing whether configs are generated as expected.

    Returns:
        Dict[str, Dict[str, str]]: the expected matcha configuration.
    """
    config = {
        "remote_state_bucket": {
            "account_name": "test_account_name",
            "container_name": "test_container_name",
            "client_id": "test_client_id",
        }
    }
    return config


def assert_infrastructure(
    destination_path: str,
    expected_tf_vars: Dict[str, str],
):
    """Assert if the infrastructure configuration is valid.

    Args:
        destination_path (str): infrastructure config destination path
        expected_tf_vars (Dict[str, str]): expected Terraform variables
    """
    # Test that destination path is a directory
    assert os.path.exists(destination_path)

    for module_file_name in glob.glob(os.path.join(TEMPLATE_DIR, "*.tf")):
        module_file_path = os.path.join(destination_path, module_file_name)
        assert os.path.exists(module_file_path)

    for module_name in SUBMODULE_NAMES:
        for module_file_name in glob.glob(
            os.path.join(TEMPLATE_DIR, module_name, "*.tf")
        ):
            module_file_path = os.path.join(
                destination_path, module_name, module_file_name
            )
            assert os.path.exists(module_file_path)

    # Check that Terraform variables file exists and content is equal/correct
    variables_file_path = os.path.join(destination_path, "terraform.tfvars.json")
    assert os.path.exists(variables_file_path)

    with open(variables_file_path) as f:
        tf_vars = json.load(f)

    assert tf_vars == expected_tf_vars


def assert_matcha_config(
    project_root_path: str,
    expected_config: Dict[str, Dict[str, str]],
):
    """Assert if the matcha configuration is valid.

    Args:
        project_root_path (str): the root of the project, where the matcha configuration should live
        expected_config (Dict[str, Dict[str, str]]): expected matcha configurations
    """
    # Check that Terraform variables file exists and content is equal/correct
    matcha_config_file_path = os.path.join(project_root_path, "matcha.config.json")
    assert os.path.exists(matcha_config_file_path)

    with open(matcha_config_file_path) as f:
        matcha_config = json.load(f)

    assert matcha_config == expected_config


def test_provision_state_storage(
    matcha_testing_directory: str, expected_matcha_config: Dict[str, Dict[str, str]]
):
    """Test that provision_state_storage behaves as expected.

    We do not want to provision any resources in real environment.
    We will test whether the expected template for the infrastructure is created instead.

    Args:
        matcha_testing_directory (str): temporary working directory for tests.
        expected_matcha_config (Dict[str, Dict[str, str]]): the expected matcha config.
    """
    os.chdir(matcha_testing_directory)
    remote_state_manager = RemoteStateManager(
        os.path.join(matcha_testing_directory, DEFAULT_CONFIG_NAME)
    )

    remote_state_manager.provision_state_storage("uksouth", "matcha")

    state_storage_destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure/remote_state_storage"
    )

    state_storage_expected_tf_vars = {
        "location": "uksouth",
        "prefix": "matcha",
    }

    assert_infrastructure(
        state_storage_destination_path, state_storage_expected_tf_vars
    )

    assert_matcha_config(matcha_testing_directory, expected_matcha_config)


def test_deprovision_state_storage(capsys: SysCapture) -> None:
    """Test whether deprovision state storage behaves as expected.

    Args:
        capsys (SysCapture): fixture to capture stdout and stderr
    """
    with patch(
        "matcha_ml.templates.run_state_storage_template.TemplateRunner.deprovision"
    ) as destroy:
        destroy.return_value = None
        remote_state_manager = RemoteStateManager()

        remote_state_manager.deprovision_state_storage()

        captured = capsys.readouterr()

        expected_output = "Destroying remote state management is complete!"

        assert expected_output in captured.out


def test_write_matcha_config(
    matcha_testing_directory: str, expected_matcha_config: Dict[str, Dict[str, str]]
):
    """Test whether the write_matcha_config() function is able to write the expected config to the expected destination.

    Args:
        matcha_testing_directory (str): temporary working directory for tests.
        expected_matcha_config (Dict[str, Dict[str, str]]): the expected matcha config.
    """
    os.chdir(matcha_testing_directory)
    remote_state_manager = RemoteStateManager(
        os.path.join(matcha_testing_directory, DEFAULT_CONFIG_NAME)
    )

    remote_state_manager._write_matcha_config(
        "test_account_name", "test_container_name", "test_client_id"
    )

    assert_matcha_config(matcha_testing_directory, expected_matcha_config)
