"""Reusable fixtures for test_remote_state_manager."""
from unittest.mock import patch

import pytest

from matcha_ml.templates.run_state_storage_template import (
    TemplateRunner as StateStorageTemplateRunner,
)

INTERNAL_FUNCTION_STUB = "matcha_ml.state.remote_state_manager.TemplateRunner"


@pytest.fixture(scope="class", autouse=True)
def mocked_state_storage_template_runner() -> StateStorageTemplateRunner:
    """The Template Runner with mocked variables.

    Returns:
        TemplateRunner: the mocked TemplateRunner.
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}._initialize_terraform") as initialize, patch(
        f"{INTERNAL_FUNCTION_STUB}._apply_terraform"
    ) as apply, patch(
        f"{INTERNAL_FUNCTION_STUB}._check_terraform_installation"
    ) as check_tf_install, patch(
        f"{INTERNAL_FUNCTION_STUB}._validate_terraform_config"
    ) as validate_tf_config, patch(
        f"{INTERNAL_FUNCTION_STUB}._get_terraform_output"
    ) as get:
        initialize.return_value = None
        apply.return_value = None
        check_tf_install.return_value = None
        validate_tf_config.return_value = None
        get.return_value = (
            "test-account",
            "test-container",
            "test-rg",
        )

        yield StateStorageTemplateRunner()
