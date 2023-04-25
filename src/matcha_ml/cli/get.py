"""Get command CLI."""
import json
import os

import typer

app = typer.Typer()


class ResourceStack:
    """Resource object class."""

    deployment_exists = False

    def __init__(self) -> None:
        """ResourceStack constructor."""
        # self.deployment_exists = check_current_deployment_exists()
        self.deployment_exists = True

        if not self.deployment_exists:
            return

        current_dir = os.getcwd()
        with open(f"{current_dir}/.matcha/infrastructure/matcha.state") as f:
            self.json_data = json.load(f)

    def get_resource_group(self) -> None:
        """ "Gets the resource group information."""
        return self.json_data.get("resource-group-name")


@app.callback(invoke_without_command=True)
def default_callback(context: typer.Context) -> None:
    """Default callback for get command.

    Args:
    context (typer.Context): data about the current execution.
    """
    if context.invoked_subcommand is None and stack.deployment_exists:
        stack = ResourceStack()
        print(stack.json_data)


@app.command(name="resource-group")
def resource_group() -> None:
    """Gets the resource group information."""
    stack = ResourceStack()
    if stack.deployment_exists:
        print(f"The resource group name is: {stack.get_resource_group()}")
