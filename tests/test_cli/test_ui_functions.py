"""Tests for cli.ui.functions."""

from unittest import mock

from matcha_ml.cli.ui.functions import get_modify_resource_approval


def test_get_modify_resource_approvals():
    """Test if is_approved behaves as expected based on user's input."""
    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True
        assert get_modify_resource_approval("provision", [])

        mock_confirm.return_value = False
        assert not get_modify_resource_approval("provision", [])
