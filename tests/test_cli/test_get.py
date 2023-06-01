"""Test suite to test the provision command and all its subcommands."""
import json
import os
from typing import Dict, Iterable, List
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from matcha_ml.cli.cli import app


@pytest.fixture(autouse=True)
def mock_provisioned_remote_state() -> Iterable[MagicMock]:
    """Mock remote state manager to have state provisioned.

    Returns:
        MagicMock: mock of an RemoteStateManager instance
    """
    with patch("matcha_ml.cli.cli.RemoteStateManager") as mock_state_manager_class:
        mock_state_manager = mock_state_manager_class.return_value
        mock_state_manager.is_state_provisioned.return_value = True
        yield mock_state_manager


@pytest.fixture(autouse=True)
def mock_state_file(matcha_testing_directory: str):
    """A fixture for mocking a test state file in the test directory.

    Args:
        matcha_testing_directory (str): the test directory
    """
    os.chdir(matcha_testing_directory)

    matcha_infrastructure_dir = os.path.join(".matcha", "infrastructure", "resources")
    os.makedirs(matcha_infrastructure_dir)
    matcha_state_path = os.path.join(".matcha", "infrastructure", "matcha.state")

    state_file_resources = {
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "zenml_test_connection_string",
            "server-password": "zen_server_password",
            "server-url": "zen_server_url",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
    }

    with open(matcha_state_path, "w") as f:
        json.dump(state_file_resources, f)


@pytest.fixture
def expected_output_lines() -> List[str]:
    """The expected output on cli with hidden sensitive value in default output format.

    The format of the output is a list, which allows each item in the list to be treated as a line for easier assertion in the test.

    Returns:
        List[str]: expected output with sensitive value hidden
    """
    output_lines = [
        "Pipeline",
        "- flavor: zenml",
        "- connection-string: ********",
        "- server-password: *******",
        "- server-url: zen_server_url",
        "Experiment tracker",
        "- flavor: mlflow",
        "- tracking-url: mlflow_test_url",
    ]

    return output_lines


@pytest.fixture
def expected_outputs_json() -> Dict[str, Dict[str, str]]:
    """The expected output on cli with hidden sensitive value in json output format.

    Returns:
        dict: expected output with sensitive value hidden in JSON output format
    """
    outputs = {
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "********",
            "server-password": "********",
            "server-url": "zen_server_url",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
    }

    return outputs


@pytest.fixture
def expected_output_lines_yaml() -> List[str]:
    """The expected output on cli with hidden sensitive value in yaml output format.

    The format of the output is a list, which allows each item in the list to be treated as a line for easier assertion in the test.

    Returns:
        List[str]: expected output with sensitive value hidden in yaml output format
    """
    output_lines = [
        "experiment-tracker:",
        "flavor: mlflow",
        "tracking-url: mlflow_test_url",
        "pipeline:",
        "connection-string: '********'",
        "flavor: zenml",
        "server-password: '********'",
        "server-url: zen_server_url",
    ]

    return output_lines


def test_cli_get_command_help(runner: CliRunner):
    """Test cli for get command help.

    Args:
        runner (CliRunner): typer CLI runner
    """
    # Invoke get command
    result = runner.invoke(app, ["get", "--help"])

    # Exit code 0 means there was no error
    assert result.exit_code == 0

    # Assert string is present in cli output
    assert "Get information for the provisioned resources." in result.stdout


def test_cli_get_command_with_no_state_file(
    runner: CliRunner, mock_provisioned_remote_state: MagicMock
):
    """Test cli for get command when the state file does not exist.

    Args:
        runner (CliRunner): typer CLI runner
        mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
    """
    state_file_path = os.path.join(".matcha", "infrastructure", "matcha.state")
    os.remove(state_file_path)

    # Invoke get command
    result = runner.invoke(app, ["get"])

    assert result.exit_code == 0
    assert "Error - matcha.state file does not exist at" in str(result.stdout)

    mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_hide_sensitive(
#     runner: CliRunner,
#     expected_output_lines: List[str],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli get command when getting all resources with no `show-sensitive` option specified.

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_output_lines (List[str]): expected output with sensitive value hidden
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     result = runner.invoke(app, ["get"])

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0

#     for line in expected_output_lines:
#         assert line in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_show_sensitive(
#     runner: CliRunner,
#     expected_output_lines: List[str],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli for get command when getting all resources with show-sensitive` option specified.

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_output_lines (List[str]): expected output with sensitive value hidden
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     result = runner.invoke(app, ["get", "--show-sensitive"])

#     # Override fixture to expose sensitive value.
#     expected_output_lines[2] = "- connection-string: zenml_test_connection_string"
#     expected_output_lines[3] = "- server-password: zen_server_password"

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0

#     for line in expected_output_lines:
#         assert line in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_with_resource(
#     runner: CliRunner,
#     expected_output_lines: List[str],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli for get command with a specified resource.

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_output_lines (List[str]): expected output with sensitive value hidden
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     # Invoke get command
#     result = runner.invoke(app, ["get", "experiment-tracker"])

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0

#     # expected_output_lines[5:] only includes the experiment-tracker resources.
#     for line in expected_output_lines[5:]:
#         assert line in result.stdout

#     # expected_output_lines[:5] checks that pipeline resources are not included in the output.
#     for line in expected_output_lines[:5]:
#         assert line not in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_with_invalid_resource_name(
#     runner: CliRunner, mock_provisioned_remote_state: MagicMock
# ):
#     """Test cli for get command with a resource name that does not exist in the state file.

#     Args:
#         runner (CliRunner): typer CLI runner
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     # Invoke get command
#     result = runner.invoke(app, ["get", "does-not-exist"])

#     assert result.exit_code == 0
#     assert (
#         "Error - a resource type with the name 'does-not-exist' does not exist."
#         in result.stdout
#     )

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_with_resource_and_property(
#     runner: CliRunner,
#     expected_output_lines: List[str],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli for get command with a specified resource and resource property in default output format.

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_output_lines (List[str]): expected output with sensitive value hidden
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     # Invoke get command
#     result = runner.invoke(app, ["get", "experiment-tracker", "tracking-url"])

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0

#     # expected_output_lines[-1] includes only the tracking-url
#     for line in expected_output_lines[-1]:
#         assert line in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_with_resource_and_property_json(
#     runner: CliRunner,
#     expected_outputs_json: Dict[str, Dict[str, str]],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli for get command with a specified resource and resource property in JSON output format.

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_outputs_json (dict): expected output with sensitive value hidden in JSON output format
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     expected_output = json.dumps(
#         expected_outputs_json["experiment-tracker"]["tracking-url"], indent=2
#     )

#     # Invoke get command
#     result = runner.invoke(
#         app, ["get", "experiment-tracker", "tracking-url", "--output", "json"]
#     )

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0
#     # Assert JSON is present and correct in cli output
#     assert expected_output in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_json_no_show_sensitive(
#     runner: CliRunner,
#     expected_outputs_json: Dict[str, Dict[str, str]],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli get command default in JSON output with no `show-sensitive` option specified.

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_outputs_json (dict): expected output with sensitive value hidden in JSON output format
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     expected_output = json.dumps(expected_outputs_json, indent=2)

#     # Invoke get command
#     result = runner.invoke(app, ["get", "--output", "json"])

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0
#     # Assert JSON is present and correct in cli output
#     assert expected_output in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_yaml_no_show_sensitive(
#     runner: CliRunner,
#     expected_output_lines_yaml: List[str],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli get command default in YAML output with `show-sensitive` option specified..

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_output_lines_yaml (List[str]): expected output with sensitive value hidden in yaml output format
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     # Invoke get command
#     result = runner.invoke(app, ["get", "--output", "yaml"])

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0
#     # Assert YAML is present and correct in cli output
#     for line in expected_output_lines_yaml:
#         assert line in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_json_show_sensitive(
#     runner: CliRunner,
#     expected_outputs_json: Dict[str, Dict[str, str]],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli get command default in JSON output with `show-sensitive` option specified..

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_outputs_json (dict): expected output with sensitive value hidden in JSON output format
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     expected_outputs_json["pipeline"][
#         "connection-string"
#     ] = "zenml_test_connection_string"
#     expected_outputs_json["pipeline"]["server-password"] = "zen_server_password"

#     expected_output = json.dumps(expected_outputs_json, indent=2)

#     # Invoke get command
#     result = runner.invoke(app, ["get", "--output", "json", "--show-sensitive"])

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0
#     # Assert JSON is present and correct in cli output
#     assert expected_output in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_yaml_show_sensitive(
#     runner: CliRunner,
#     expected_output_lines_yaml: List[str],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli get command default in YAML output with `show-sensitive` option specified..

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_output_lines_yaml (List[str]): expected output with sensitive value hidden in yaml output format
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     # Override fixture to expose sensitive value.
#     expected_output_lines_yaml[4] = "connection-string: zenml_test_connection_string"
#     expected_output_lines_yaml[6] = "server-password: zen_server_password"

#     # Invoke get command
#     result = runner.invoke(app, ["get", "--output", "yaml", "--show-sensitive"])

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0
#     # Assert YAML is present and correct in cli output
#     for line in expected_output_lines_yaml:
#         assert line in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_no_show_sensitive_with_sensitive_resource(
#     runner: CliRunner,
#     expected_output_lines: List[str],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli get command for when getting resource with sensitive value with no `show-sensitive` option specified.

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_output_lines (List[str]): expected output with sensitive value hidden
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     result = runner.invoke(app, ["get", "pipeline"])

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0

#     # expected_output_lines[:5] does not include experiment tracker.
#     for line in expected_output_lines[:5]:
#         assert line in result.stdout

#     # expected_output_lines[5:] checks experiment tracker not in output.
#     for line in expected_output_lines[5:]:
#         assert line not in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()


# def test_cli_get_command_show_sensitive_with_resource(
#     runner: CliRunner,
#     expected_output_lines: List[str],
#     mock_provisioned_remote_state: MagicMock,
# ):
#     """Test cli get command for when getting resource with sensitive value with `show-sensitive` option specified.

#     Args:
#         runner (CliRunner): typer CLI runner
#         expected_output_lines (List[str]): expected output with sensitive value hidden
#         mock_provisioned_remote_state (MagicMock): mock of an RemoteStateManager instance
#     """
#     result = runner.invoke(app, ["get", "pipeline", "--show-sensitive"])

#     # Override fixture to expose sensitive value.
#     expected_output_lines[2] = "- connection-string: zenml_test_connection_string"
#     expected_output_lines[3] = "- server-password: zen_server_password"

#     # Exit code 0 means there was no error
#     assert result.exit_code == 0

#     # expected_output_lines[:5] does not include experiment tracker.
#     for line in expected_output_lines[:5]:
#         assert line in result.stdout

#     # expected_output_lines[5:] checks experiment tracker not in output.
#     for line in expected_output_lines[5:]:
#         assert line not in result.stdout

#     mock_provisioned_remote_state.use_lock.assert_called_once()
