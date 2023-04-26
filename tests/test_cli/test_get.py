"""Test suite to test the provision command and all its subcommands."""
import json
import os

from typer.testing import CliRunner

from matcha_ml.cli.cli import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def test_cli_get_command_help(runner: CliRunner):
    """Test cli for get command help.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke get command
    result = runner.invoke(app, ["get", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    print(result.stdout)

    # Assert string is present in cli output
    assert (
        " The get command. Default: prints all information about the current"
        in result.stdout
    )


def test_cli_get_command(
    runner,
    matcha_testing_directory,
):
    """Test get command to print the current information about the deployed resources.

    Args:
        runner (CliRunner): typer CLI runner
        matcha_testing_directory (str): temporary working directory
    """
    os.chdir(matcha_testing_directory)

    matcha_infrastructure_dir = os.path.join(".matcha", "infrastructure")
    os.makedirs(matcha_infrastructure_dir)

    terraform_outputs = {
        "mlflow_tracking_url": "mlflow_test_url",
        "zenml_storage_path": "zenml_test_storage_path",
        "zenml_connection_string": "zenml_test_connection_string",
        "k8s_context": "k8s_test_context",
        "azure_container_registry": "azure_container_registry",
        "azure_registry_name": "azure_registry_name",
        "zen_server_url": "zen_server_url",
        "zen_server_username": "zen_server_username",
        "zen_server_password": "zen_server_password",
        "seldon_workloads_namespace": "test_seldon_workloads_namespace",
        "seldon_base_url": "test_seldon_base_url",
        "resource_group_name": "test_resources",
    }

    with open("matcha.state", "w") as f:
        json.dump(terraform_outputs, f)

    # Invoke provision command
    result = runner.invoke(app, ["get"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0
    print(result.stdout)
    assert False
