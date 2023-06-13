"""Test for core.destroy."""

from unittest.mock import patch

import pytest

from matcha_ml.core.core import destroy
from matcha_ml.errors import MatchaError

CORE_FUNCTION_STUB = "matcha_ml.core.core"


@patch(f"{CORE_FUNCTION_STUB}.AzureRunner")
@patch(f"{CORE_FUNCTION_STUB}.RemoteStateManager")
def test_destroy_with_state_provisioned(
    mocked_remote_state_manager_class, mocked_azure_runner_class
):
    """Test the core destroy function when state is provisioned.

    Args:
        mocked_remote_state_manager_class (RemoteStateManager): a mocked RemoteStateManager class.
        mocked_azure_runner_class (AzureRunner): a mocked AzureRunner class.
    """
    mocked_remote_state_manager = mocked_remote_state_manager_class.return_value
    mocked_azure_runner = mocked_azure_runner_class.return_value

    mocked_remote_state_manager.is_state_provisioned.return_value = True

    destroy()

    mocked_remote_state_manager_class.assert_called_once()
    mocked_azure_runner_class.assert_called_once()

    mocked_remote_state_manager.use_lock.assert_called_once()
    mocked_remote_state_manager.use_remote_state.assert_called_once()
    mocked_azure_runner.deprovision.assert_called_once()
    mocked_remote_state_manager.deprovision_remote_state.assert_called_once()


@patch(f"{CORE_FUNCTION_STUB}.RemoteStateManager")
def test_destroy_error_handling(mocked_remote_state_manager_class):
    """Test the core destroy function when state is not provisioned.

    Args:
        mocked_remote_state_manager_class (RemoteStateManager): a mocked RemoteStateManager class.
    """
    mocked_remote_state_manager = mocked_remote_state_manager_class.return_value

    mocked_remote_state_manager.is_state_provisioned.return_value = False

    with pytest.raises(MatchaError):
        destroy()

    mocked_remote_state_manager_class.assert_called_once()

    mocked_remote_state_manager.use_lock.assert_called_once()
    mocked_remote_state_manager.use_remote_state.assert_called_once()
    mocked_remote_state_manager.deprovision_remote_state.assert_not_called()
