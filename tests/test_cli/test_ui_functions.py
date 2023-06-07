"""Tests for cli.ui.functions."""

from unittest import mock

from matcha_ml.cli.ui.functions import is_approved


def test_is_approved():
    """Test if is_approved behaves as expected based on user's input."""
    with mock.patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = True
        assert is_approved("provision", [])

        mock_confirm.return_value = False
        assert not is_approved("provision", [])
