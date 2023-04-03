"""Tests for spinner."""
from unittest import mock

from matcha_ml.cli.ui.spinner import Spinner


def test_spinner():
    """Test spinner uses rich Progress correctly."""
    with mock.patch("matcha_ml.cli.ui.spinner.Progress") as mock_progress_class:
        mock_progress = mock_progress_class.return_value

        mock_progress.start.assert_not_called()
        mock_progress.stop.assert_not_called()
        with Spinner("Test spinner"):
            mock_progress.add_task.assert_called_with(
                description="Test spinner", total=None
            )
            mock_progress.start.assert_called()
            mock_progress.stop.assert_not_called()

        mock_progress.stop.assert_called()
