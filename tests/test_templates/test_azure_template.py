"""Test suite to test the azure template."""

import pytest

from matcha_ml.templates import AzureTemplate


@pytest.fixture
def azure_template() -> AzureTemplate:
    """Azure template object for testing.

    Returns:
        AzureTemplate: the Azure template.
    """
    return AzureTemplate()


# def test_check_current_configuration_is_provisioned()
# TODO
