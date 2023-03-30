"""Unit test for functions from ui_functions."""
from typing import List, Optional, Tuple

import pytest

from matcha_ml.cli.ui_primitives.ui_functions import build_resource_confirmation


@pytest.mark.parametrize(
    "header, resources, footer, expected",
    [
        (
            "Header",
            [("Resource Name 1", "Description 1")],
            None,
            "Header:\n" "1. [yellow]Resource Name 1[/yellow]: Description 1\n",
        ),
        (
            "Header",
            [
                ("Resource Name 1", "Description 1"),
                ("Resource Name 2", "Description 2"),
            ],
            None,
            "Header:\n"
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
            "Header:\n"
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
