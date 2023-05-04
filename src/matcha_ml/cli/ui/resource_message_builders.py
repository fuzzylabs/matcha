"""UI resource message builders."""
import json
from typing import Dict, Optional

import yaml
from rich.console import Console

err_console = Console(stderr=True)

SENSITIVE_OUTPUT = ["connection-string", "server-username", "server-password"]


def dict_to_json(resources: Dict[str, Dict[str, str]]) -> str:
    """Return the resources as str in JSON format.

    Args:
        resources (Dict[str, str]): resources in the format of a dictionary.

    Returns:
        str: resources as str in JSON format.
    """
    return json.dumps(resources, indent=4)


def dict_to_yaml(resources: Dict[str, Dict[str, str]]) -> str:
    """Return the resources as str in YAML format.

    Args:
        resources (Dict[str, str]): resources in the format of a dictionary.

    Returns:
        str: resources as str in YAML format.
    """
    return str(yaml.dump(resources))


def build_resource_output(
    resources: Dict[str, Dict[str, str]],
    output_format: Optional[str] = None,
) -> str:
    """Build the output of the resource based on the format specified by the user.

    Args:
        resources (Dict[str, str]): a dictionary of resources.
        output_format (Optional[str], optional): the format of the resource output specified by the user. Defaults to None.

    Returns:
        str: the resource output in the format as a string.
    """
    if output_format == "json":
        return dict_to_json(resources)
    elif output_format == "yaml":
        return dict_to_yaml(resources)
    else:
        message = "\nBelow are the resources provisioned.\n\n"

        for resource_name, properties in resources.items():
            message += f"{resource_name.replace('-', ' ').capitalize()}\n"

            for property_name, property_value in properties.items():
                message += f"   - {property_name}: {property_value}\n"

            message += "\n"

        return message


def hide_sensitive_in_output(
    resource_output_dict: Dict[str, Dict[str, str]]
) -> Dict[str, Dict[str, str]]:
    """Hides the sensitive resource property values for provisioned resources.

    Args:
        resource_output_dict (Dict[str, Dict[str, str]]): all resource outputs in the format of a dictionary.

    Returns:
        Dict[str, Dict[str, str]]: resource outputs without sensitive value.
    """
    for _, properties in resource_output_dict.items():
        for property_name in properties:
            if property_name in SENSITIVE_OUTPUT:
                properties[property_name] = "********"

    return resource_output_dict
