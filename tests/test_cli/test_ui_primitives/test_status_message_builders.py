"""Unit test for functions from ui_functions."""
from typing import List, Optional, Tuple

import pytest

from matcha_ml.cli.ui.status_message_builders import (
    build_resource_confirmation,
    build_status,
    build_step_success_status,
    build_substep_success_status
)


@pytest.mark.parametrize(
    "header, resources, footer, expected",
    [
        (
            "Header",
            [("Resource Name 1", "Description 1")],
            None,
            "\nHeader:\n\n1. [yellow]Resource Name 1[/yellow]: Description 1\n",
        ),
        (
            "Header",
            [
                ("Resource Name 1", "Description 1"),
                ("Resource Name 2", "Description 2"),
            ],
            None,
            "\nHeader:\n\n"
            "1. [yellow]Resource Name 1[/yellow]: Description 1\n"
            "2. [yellow]Resource Name 2[/yellow]: Description 2\n",
        ),
        (
            "Header",
            [
                ("Resource Name 1", "Description 1"),
                ("Resource Name 2", "Description 2"),
            ],
            "Footer",
            "\nHeader:\n\n"
            "1. [yellow]Resource Name 1[/yellow]: Description 1\n"
            "2. [yellow]Resource Name 2[/yellow]: Description 2\n"
            "\n"
            "Footer\n",
        ),
    ],
)
def test_build_resource_confirmation_expected_output(
    header: str, resources: List[Tuple[str, str]], footer: Optional[str], expected: str
):
    """Test expected output for build_resource_confirmation function.

    Args:
        header (str): header of the confirmation message
        resources (List[Tuple[str, str]]): a list of resource name and description pairs.
        footer (Optional[str], optional): footer of the confirmation message. Defaults to None.
        expected (str): the expected confirmation message
    """
    assert build_resource_confirmation(header, resources, footer) == expected


def test_build_status():
    """Test build status formats status message correctly."""
    expected = "[bright_white]Some status[/bright_white]"
    assert build_status("Some status") == expected


def test_build_step_success_status():
    """Test build step success status formats status message correctly."""
    expected = "[green bold]Step finished![/green bold]"
    assert build_step_success_status("Step finished!") == expected


def test_build_substep_success_status():
    """Test build substep success status formats status message correctly."""
    expected = "[green]Step finished![/green]"
    assert build_substep_success_status("Step finished!") == expected