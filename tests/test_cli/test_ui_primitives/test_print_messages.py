from unittest import mock

from matcha_ml.cli.ui.print_messages import print_status


def test_print_status():
    with mock.patch("rich.print") as mock_print:
        print_status("[white]Some status[/white]")
        mock_print.assert_called_with("[white]Some status[/white]")


def test_print_error():
    ...
