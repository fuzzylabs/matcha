"""Test suite to test the azure template."""
import glob
import json
import os
from typing import Dict

import pytest

from matcha_ml.templates.build_templates.azure_template import (
    SUBMODULE_NAMES,
    TemplateVariables,
    build_template,
    verify_azure_location,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)


@pytest.fixture
def template_src_path() -> str:
    """Fixture for the test infrastructure template path.

    Returns:
        str: template path
    """
    return TEMPLATE_DIR


def assert_infrastructure(destination_path: str, expected_tf_vars: Dict[str, str]):
    """Assert if the infrastructure configuration is valid

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

    with open(variables_file_path, "r") as f:
        tf_vars = json.load(f)

    assert tf_vars == expected_tf_vars


def test_build_template(matcha_testing_directory, template_src_path):
    """Test that the template is built and copied to correct locations.

    Args:
        matcha_testing_directory (str): Temporary .matcha directory path
        template_src_path (str): Existing template directory path
    """
    config = TemplateVariables("uksouth")

    destination_path = os.path.join(matcha_testing_directory, "infrastructure")

    build_template(config, template_src_path, destination_path)

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)


@pytest.mark.parametrize(
    "location_name, expectation",
    [
        ("ukwest", True),  # Valid location
        ("mordorwest", False),  # Invalid location
    ],
)
def test_verify_azure_location(
    location_name: str, expectation: pytest.raises, monkeypatch
):
    """Test that Azure location is being correctly verified.

    Args:
        monkeypatch (pytest.monkeypatch.MonkeyPatch): Pytest monkeypatch for patching a function
    """

    def mock_get_azure_locations() -> list:
        """Mock function for getting a list of Azure locations.

        Returns:
            list: Mock list of locations
        """
        return ["ukwest", "uksouth"]

    monkeypatch.setattr(
        "matcha_ml.templates.build_templates.azure_template.get_azure_locations",
        mock_get_azure_locations,
    )

    assert verify_azure_location(location_name) is expectation
