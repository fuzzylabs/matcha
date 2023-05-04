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
    ) as apply, patch(f"{INTERNAL_FUNCTION_STUB}._show_terraform_outputs") as show:
        initialize.return_value = None
        apply.return_value = None
        show.return_value = None

        yield TemplateRunner()
