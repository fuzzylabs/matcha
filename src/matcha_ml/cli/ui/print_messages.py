"""UI print functions."""
import json
from typing import Optional

import rich
from rich.console import Console

err_console = Console(stderr=True)

SENSITIVE_OUTPUT = {
    "zenml": ["connection-string", "server-username", "server-password"]
}


def print_status(status: str) -> None:
    """Print an already formatted status string.

    Args:
        status (str): formatted status string to print
    """
    rich.print(status)


def print_error(error: str) -> None:
    """Print an already formatted error string.

    Args:
        error (str): formatted error string to print
    """
    err_console.print(error)


def print_json(json: str) -> None:
    """Pretty print a JSON string.

    Args:
        json (str): JSON string to print
    """
    rich.print_json(json)


def print_resource_output(
    resource_output: str,
    output_format: Optional[str] = "json",
    show_sensitive: bool = False,
) -> None:
    """Print the resource output based on the output format specified by the user.

    Args:
        resource_output (str): the resource output to be printed.
        output_format (str, optional):  the format of the resource output specified by the user. Defaults to None.
        show_sensitive (bool): whether to show or hide sensitive output. Show all resource information if true.
    """
    resource_output_dict = json.loads(resource_output)
    print(type(resource_output_dict))

    if not show_sensitive:
        resource_output = hide_sensitive_in_output(resource_output_dict)

    if output_format == "json":
        print_json(resource_output)
    else:
        rich.print(resource_output)


def hide_sensitive_in_output(resource_output_dict: dict[str, dict[str, str]]) -> str:
    """Hide sensitive value in output.

    Args:
        resource_output_dict (dict): all resource outputs in the format of a dictionary.

    Returns:
        str: resource outputs without sensitive value.
    """
    for _, properties in resource_output_dict.items():
        if properties["flavor"] in SENSITIVE_OUTPUT:
            sensitive_values = SENSITIVE_OUTPUT[properties["flavor"]]
            for value_to_censor in sensitive_values:
                # properties.pop(value_to_censor, None)
                properties[value_to_censor] = "********"

    return str(json.dumps(resource_output_dict))
