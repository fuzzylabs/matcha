"""Get command CLI."""
import json

import typer
import yaml

from matcha_ml.cli import experiment_tracker


def load_state_file() -> dict:
    with open(".matcha/infrastructure/matcha.state") as f:
        return json.load(f)


app = typer.Typer()
app.add_typer(
    experiment_tracker.app,
    name="experiment-tracker",
    help="The get command. Default: prints all information about the current provisioned resources.",
)


resources = load_state_file()


def dict_subset_to_json(resources: dict, subset_keys: list):
    temp_dict = {key: resources.get(key) for key in subset_keys}
    return json.dumps(temp_dict, indent=4)


def dict_subset_to_to_yaml(resources: dict, subset_keys: list):
    temp_dict = {key: resources.get(key) for key in subset_keys}
    return yaml.dump(temp_dict)


@app.command(name="resource-group")
def resource_group(
    output: str = typer.Option(
        default=None,
    )
) -> None:
    """Gets the resource group information."""
    resource_component_names = ["resource_group_name"]
    if output == "json":
        print(dict_subset_to_json(resources, resource_component_names))
    elif output == "yaml":
        print(dict_subset_to_to_yaml(resources, resource_component_names))
    else:
        print(f"The resource group name is: {resources.get('resource_group_name')}")


@app.command(name="experiment-tracker")
def experiment_tracker() -> None:
    """Gets the resource group information."""



@app.callback(invoke_without_command=True)
def default_callback(context: typer.Context) -> None:
    """Return all the resources if no subcommand is passed.

    Args:
        context (typer.Context): data about the current execution
    """
    if context.invoked_subcommand is None:
        print(f"All the provisioned resource: {resources}")
