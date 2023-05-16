"""Test for the RemoteStateManager."""
import glob
import json
import os
from typing import Dict
from unittest.mock import patch

import typer

from matcha_ml.state.remote_state_manager import RemoteStateManager
from matcha_ml.templates.build_templates.state_storage_template import SUBMODULE_NAMES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)


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


def test_fill_provision_variables():
    """Test whether the fill_provision_variables function returns the expected value based on inputs."""
    remote_state_manager = RemoteStateManager()

    expected_location = "test_location"
    expected_prefix = "test_prefix"

    location, prefix = remote_state_manager.fill_provision_variables(
        "test_location", "test_prefix"
    )

    assert location == expected_location
    assert prefix == expected_prefix

    with patch.object(
        typer, "prompt", side_effect=[expected_location, expected_prefix]
    ):
        location, prefix = remote_state_manager.fill_provision_variables("", "")

    assert location == expected_location
    assert prefix == expected_prefix


def test_provision_state_storage(matcha_testing_directory):
    """Test that provision_state_storage behaves as expected.

    We do not want to provision any resources in real environment.
    We will test whether the expected template for the infrastructure is created instead.

    Args:
        matcha_testing_directory (str): temporary working directory for tests.
    """
    os.chdir(matcha_testing_directory)
    remote_state_manager = RemoteStateManager()

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
