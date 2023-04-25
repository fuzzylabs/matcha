"""Get command CLI."""
import json

import typer
import yaml

# from rich import print
from matcha_ml.cli import experiment_tracker

# class ResourceStack:
#     """Resource object class."""

#     deployment_exists = False

#     def __init__(self) -> None:
#         """ResourceStack constructor."""
#         self.deployment_exists = check_current_deployment_exists()
#         self.deployment_exists = True

#         if not self.deployment_exists:
#             return

#         current_dir = os.getcwd()
#         with open(f"{current_dir}/.matcha/infrastructure/matcha.state") as f:
#             self.json_data = json.load(f)

#     def get_resource_group(self) -> None:
#         """ "Gets the resource group information."""
#         return self.json_data.get("resource_group_name")

#     def get_all_resource(self) -> None:
#         return self.json_data

#     def get_experiment_tracker(self) -> None:
#         experiment_tracker_resource = {}

#         experiment_tracker_resource["url"] = self.json_data.get("mlflow_tracking_url")
#         return experiment_tracker


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


def to_json(resources: dict, names: list):
    temp_dict = {name: resources.get(name) for name in names}
    return json.dumps(temp_dict, indent=4)


def to_yaml(resources: dict, names: list):
    temp_dict = {name: resources.get(name) for name in names}
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
        # to_json(resources, "resource_group_name")
        print(to_json(resources, resource_component_names))
    elif output == "yaml":
        print(to_yaml(resources, resource_component_names))
    else:
        print(f"The resource group name is: {resources.get('resource_group_name')}")


# @app.command(name="experiment-tracker")
# def experiment_tracker(resources=resources) -> None:
#     """Gets the resource group information."""
#     experiment_tracker.app.call_command("url", resources=resources)


@app.callback(invoke_without_command=True)
def default_callback(context: typer.Context) -> None:
    """Return all the resources if no subcommand is passed.

    Args:
        context (typer.Context): data about the current execution
    """
    if context.invoked_subcommand is None:
        print(f"All the provisioned resource: {resources}")
