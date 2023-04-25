"""UI resource message builders."""
import json
from typing import Dict, Optional

import yaml
from rich.console import Console

err_console = Console(stderr=True)


def dict_to_json(resources: Dict[str, str]) -> str:
    """Return the resources as str in JSON format.

    Args:
        resources (Dict[str, str]): resources in the format of a dictionary.

    Returns:
        str: resources as str in JSON format.
    """
    return json.dumps(resources, indent=4)


def dict_to_yaml(resources: Dict[str, str]) -> str:
    """Return the resources as str in YAML format.

    Args:
        resources (Dict[str, str]): resources in the format of a dictionary.

    Returns:
        str: resources as str in YAML format.
    """
    return str(yaml.dump(resources))


def build_resource_output(
    resources: Dict[str, str],
    output_format: Optional[str] = None,
    header: Optional[str] = None,
) -> str:
    """Build the output of the resource based on the format specified by the user.

    Args:
        resources (Dict[str, str]): a dictionary of resources.
        output_format (Optional[str], optional): the format of the resource output specified by the user. Defaults to None.
        header (Optional[str], optional): header of the resource output.

    Returns:
        str: the resource output in the format as a string.
    """
    if output_format == "json":
        return dict_to_json(resources)
    elif output_format == "yaml":
        return dict_to_yaml(resources)
    else:
        message = "" if header is None else f"\n{header}:\n\n"

        for key, value in resources.items():
            message += f"The {key.replace('_', ' ')} is: {value}\n"

        return message
