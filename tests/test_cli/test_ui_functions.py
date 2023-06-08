"""Tests for cli.ui.functions."""

from unittest import mock

from matcha_ml.cli.ui.user_approval_functions import is_user_approved


def test_user_approves():
    """Test if is_user_approved behaves as expected where user provides approval."""
    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True
        assert is_user_approved("provision", [])


def test_user_does_approves():
    """Test if is_user_approved behaves as expected where user does not provide approval."""
    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False
        assert not is_user_approved("provision", [])
