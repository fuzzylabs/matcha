"""Tests for print functions."""
from unittest import mock

from matcha_ml.cli.ui.print_messages import print_error, print_json, print_status


def test_print_status():
    """Test print_status calls correct rich methods."""
    with mock.patch("rich.print") as mock_print:
        print_status("[bright_white]Some status[/bright_white]")
        mock_print.assert_called_with("[bright_white]Some status[/bright_white]")


def test_print_error():
    """Test print_error calls correct rich methods."""
    with mock.patch("matcha_ml.cli.ui.print_messages.err_console") as mock_console:
        print_error("Some error")
        mock_console.print.assert_called_with("Some error")


def test_print_json():
    """Test print_json calls correct rich methods."""
    with mock.patch("rich.print_json") as mock_print_json:
        print_json("{}")
        mock_print_json.assert_called_with("{}")
