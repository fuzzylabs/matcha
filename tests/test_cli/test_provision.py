"""Test suite to test the provision command and all its subcommands."""
import glob
import json
import os
from typing import Dict

from matcha_ml.cli.cli import app
from src.matcha_ml.cli.provision import (
    SUBMODULE_NAMES,
    TemplateVariables,
    build_template,
    verify_azure_location,
)

from matcha_ml.templates.build_templates.azure_template import SUBMODULE_NAMES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(
    BASE_DIR, os.pardir, os.pardir, "src", "matcha_ml", "infrastructure"
)


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


def test_cli_provision_command_help(runner):
    """Test cli for provision command help.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke provision command
    result = runner.invoke(app, ["provision", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Provision cloud resources with a template." in result.stdout


def test_cli_provision_command(runner, matcha_testing_directory, monkeypatch):
    """Test provision command to copy the infrastructure template.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        monkeypatch (pytest.monkeypatch.MonkeyPatch): Pytest monkeypatch for patching a function
    """

    def mock_verify_azure_location(location):
        return True

    monkeypatch.setattr(
        "matcha_ml.cli.provision.verify_azure_location", mock_verify_azure_location
    )

    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(app, ["provision"], input="\nuksouth\nno\n")

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_args(runner, matcha_testing_directory, monkeypatch):
    """Test provision command to copy the infrastructure template with command-line arguments.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        monkeypatch (pytest.monkeypatch.MonkeyPatch): Pytest monkeypatch for patching a function

    """

    def mock_verify_azure_location(location):
        return True

    monkeypatch.setattr(
        "matcha_ml.cli.provision.verify_azure_location", mock_verify_azure_location
    )

    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(
        app, ["provision", "--location", "uksouth", "--prefix", "matcha"], input="no\n"
    )

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "uksouth", "prefix": "matcha"}

    assert_infrastructure(destination_path, expected_tf_vars)


def test_cli_provision_command_with_prefix(
    runner, matcha_testing_directory, monkeypatch
):
    """Test provision command to copy the infrastructure template with different prefix.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
        monkeypatch (pytest.monkeypatch.MonkeyPatch): Pytest monkeypatch for patching a function
    """

    def mock_verify_azure_location(location):
        return True

    monkeypatch.setattr(
        "matcha_ml.cli.provision.verify_azure_location", mock_verify_azure_location
    )

    os.chdir(matcha_testing_directory)

    # Invoke provision command
    result = runner.invoke(app, ["provision"], input="coffee\nukwest\nno\n")

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    destination_path = os.path.join(
        matcha_testing_directory, ".matcha", "infrastructure"
    )

    expected_tf_vars = {"location": "ukwest", "prefix": "coffee"}

    assert_infrastructure(destination_path, expected_tf_vars)


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


def test_cli_provision_command_with_verbose_arg(
    runner, matcha_testing_directory, monkeypatch
):
    """Test that the verbose argument works and provision shows more output.

    Args:
        runner (CliRunner): type CLI runner
        matcha_testing_directory (str): temporary working directory
        monkeypatch (pytest.monkeypatch.MonkeyPatch): Pytest monkeypatch for patching a function
    """

    def mock_verify_azure_location(location):
        """Mock verify Azure location function

        Args:
            location (str): Location string to check

        Returns:
            bool: Mock verificaiton bool always set to True
        """
        return True

    monkeypatch.setattr(
        "matcha_ml.cli.provision.verify_azure_location", mock_verify_azure_location
    )

    os.chdir(matcha_testing_directory)

    result = runner.invoke(app, ["provision", "--verbose"], input="\nuksouth\nno")

    assert result.exit_code == 0

    for verbose_output in [
        "module configuration was copied",
        "Configuration was copied",
        "Template variables were added",
        "Template configuration has finished!",
    ]:
        assert verbose_output in result.stdout


@pytest.mark.parametrize(
    "location_name, expectation",
    [
        (
            "ukwest",
            True,
        ),  # Valid location
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
        "src.matcha_ml.cli.provision.get_azure_locations", mock_get_azure_locations
    )

    assert verify_azure_location(location_name) is expectation
