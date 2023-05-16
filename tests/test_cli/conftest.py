"""Reusable fixtures for test_cli."""
from unittest.mock import patch

import pytest

from matcha_ml.templates.run_template import TemplateRunner

INTERNAL_FUNCTION_STUBS = [
    "matcha_ml.cli.provision.TemplateRunner",
    "matcha_ml.state.remote_state_manager.TemplateRunner",
]


@pytest.fixture(scope="class", autouse=True)
def mocked_resource_template_runner() -> TemplateRunner:
    """The Template Runner with mocked variables.

    Returns:
        TemplateRunner: the mocked TemplateRunner.
    """
    with patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._initialize_terraform"
    ) as initialize, patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._apply_terraform"
    ) as apply, patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._show_terraform_outputs"
    ) as show, patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._check_terraform_installation"
    ) as check_tf_install, patch(
        f"{INTERNAL_FUNCTION_STUBS[0]}._validate_terraform_config"
    ) as validate_tf_config:
        initialize.return_value = None
        apply.return_value = None
        show.return_value = None
        check_tf_install.return_value = None
        validate_tf_config.return_value = None

        yield TemplateRunner()


@pytest.fixture(scope="class", autouse=True)
def mocked_state_storage_template_runner() -> TemplateRunner:
    """The Template Runner with mocked variables.

    Returns:
        TemplateRunner: the mocked TemplateRunner.
    """
    with patch(
        f"{INTERNAL_FUNCTION_STUBS[1]}._initialize_terraform"
    ) as initialize, patch(
        f"{INTERNAL_FUNCTION_STUBS[1]}._apply_terraform"
    ) as apply, patch(
        f"{INTERNAL_FUNCTION_STUBS[1]}._check_terraform_installation"
    ) as check_tf_install, patch(
        f"{INTERNAL_FUNCTION_STUBS[1]}._validate_terraform_config"
    ) as validate_tf_config:
        initialize.return_value = None
        apply.return_value = None
        check_tf_install.return_value = None
        validate_tf_config.return_value = None

        yield TemplateRunner()
