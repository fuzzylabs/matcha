"""Unit test for functions from ui_functions."""
from typing import List, Optional, Tuple

import pytest

from matcha_ml.cli.constants import (
    RESOURCE_MSG_CORE,
    RESOURCE_MSG_MODULES,
    STATE_RESOURCE_MSG,
)
from matcha_ml.cli.ui.status_message_builders import (
    build_resource_confirmation,
    build_resources_msg_content,
    build_status,
    build_step_success_status,
    build_substep_success_status,
)
from matcha_ml.config.matcha_config import MatchaConfigComponent
from matcha_ml.constants import DEFAULT_STACK


@pytest.fixture
def matcha_stack_component_names(
    mocked_matcha_config_stack_component: MatchaConfigComponent,
) -> list[str]:
    """A fixture to get the names of the modules in the stack.

    Args:
        mocked_matcha_config_stack_component (MatchaConfigComponent): the default stack as a component.

    Returns:
        list[str]: the names of the modules as a list.
    """
    return [
        prop.name
        for prop in mocked_matcha_config_stack_component.properties
        if prop.name != "name"
    ]


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


def test_build_resource_msg_content_expected(
    mocked_matcha_config_stack_component: MatchaConfigComponent,
    matcha_stack_component_names: list[str],
):
    """Test that the resource message has the content that we would expect for a default stack.

    Args:
        mocked_matcha_config_stack_component (MatchaConfigComponent): the default stack as a component.
        matcha_stack_component_names (list[str]): the names of the modules in the default stack.
    """
    stack_modules = [
        RESOURCE_MSG_MODULES[name] for name in matcha_stack_component_names
    ]
    expected_result = RESOURCE_MSG_CORE + stack_modules

    resource_msg = build_resources_msg_content(
        stack=mocked_matcha_config_stack_component, destroy=False
    )

    assert resource_msg == expected_result


def test_build_resource_msg_content_expected_destroy(
    mocked_matcha_config_stack_component: MatchaConfigComponent,
    matcha_stack_component_names: list[str],
):
    """Test that the resource message has the content that we would expect when destroying the default stack.

    Args:
        mocked_matcha_config_stack_component (MatchaConfigComponent): the default stack as a component.
        matcha_stack_component_names (list[str]): the names of the modules in the default stack.
    """
    stack_modules = [
        RESOURCE_MSG_MODULES[name] for name in matcha_stack_component_names
    ]
    expected_result = RESOURCE_MSG_CORE + stack_modules + STATE_RESOURCE_MSG

    resource_msg = build_resources_msg_content(
        stack=mocked_matcha_config_stack_component, destroy=True
    )

    assert resource_msg == expected_result


def test_build_resource_msg_content_no_stack():
    """Test that the resource message is accurate when no stack is specified."""
    stack_modules = [RESOURCE_MSG_MODULES[prop.name] for prop in DEFAULT_STACK]
    expected_result = RESOURCE_MSG_CORE + stack_modules

    resource_msg = build_resources_msg_content()

    assert resource_msg == expected_result


def test_build_resource_msg_content_no_stack_destroy():
    """Test that the resource messages is accurate when no stack is specific and we're destroying."""
    stack_modules = [RESOURCE_MSG_MODULES[prop.name] for prop in DEFAULT_STACK]
    expected_result = RESOURCE_MSG_CORE + stack_modules + STATE_RESOURCE_MSG

    resource_msg = build_resources_msg_content(destroy=True)

    assert resource_msg == expected_result
