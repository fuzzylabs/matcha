"""Reusable fixtures for test_cli."""
from unittest.mock import patch

import pytest

from matcha_ml.templates.run_template import TemplateRunner

INTERNAL_FUNCTION_STUB = "matcha_ml.cli.provision.TemplateRunner"


@pytest.fixture(scope="class", autouse=True)
def mocked_template_runner() -> TemplateRunner:
    """The Template Runner with mocked variables.

    Returns:
        TemplateRunner: the mocked TemplateRunner.
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}._initialize_terraform") as initialize, patch(
        f"{INTERNAL_FUNCTION_STUB}._apply_terraform"
    ) as apply, patch(
        f"{INTERNAL_FUNCTION_STUB}._show_terraform_outputs"
    ) as show, patch(
        f"{INTERNAL_FUNCTION_STUB}._check_terraform_installation"
    ) as check_tf_install, patch(
        f"{INTERNAL_FUNCTION_STUB}._validate_terraform_config"
    ) as validate_tf_config:
        initialize.return_value = None
        apply.return_value = None
        show.return_value = None
        check_tf_install.return_value = None
        validate_tf_config.return_value = None

        yield TemplateRunner()
