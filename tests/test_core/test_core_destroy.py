"""Test for core.destroy."""

from pathlib import Path
from typing import Iterable
from unittest import mock
from unittest.mock import MagicMock

import pytest

from matcha_ml.core.core import destroy
from matcha_ml.errors import MatchaError

CORE_FUNCTION_STUB = "matcha_ml.core.core"


@pytest.fixture(autouse=True)
def mock_provisioned_remote_state() -> Iterable[MagicMock]:
    """Mock remote state manager to have state provisioned.

    Returns:
        MagicMock: mock of a RemoteStateManager instance
    """
    with mock.patch(
        f"{CORE_FUNCTION_STUB}.RemoteStateManager"
    ) as mock_state_manager_class:
        mock_state_manager = mock_state_manager_class.return_value
        mock_state_manager.is_state_provisioned.return_value = True
        mock_state_manager.use_remote_state = MagicMock()
        mock_state_manager.deprovision_remote_state.return_value = MagicMock()
        yield mock_state_manager


def test_destroy_with_state_provisioned(
    mock_provisioned_remote_state: MagicMock, mock_state_file: Path
):
    """Test the core destroy function when state is provisioned.

    Args:
        mock_provisioned_remote_state (MagicMock): a mocked remote state
        mock_state_file (Path): a mocked state file in the test directory
    """
    with mock.patch(f"{CORE_FUNCTION_STUB}.AzureRunner") as azure_runner:
        runner = azure_runner.return_value
        runner.deprovision.return_value = MagicMock()

        destroy()

        runner.deprovision.assert_called()


def test_destroy_error_handling(mock_provisioned_remote_state):
    """Test the core destroy function when state is not provisioned.

    Args:
        mock_provisioned_remote_state (MagicMock): a mocked remote state.
    """
    mock_provisioned_remote_state.is_state_provisioned.return_value = False

    with pytest.raises(MatchaError):
        destroy()

    mock_provisioned_remote_state.is_state_provisioned.assert_called_once()
