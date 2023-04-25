"""Subcommands of experiment tracker."""
import json
from typing import Dict

import typer

app = typer.Typer()


def load_state_file() -> Dict[str, str]:
    """Load the matcha.state file into a dictionary.

    Returns:
        Dict[str, str]: matcha.state file in dictionary format.
    """
    with open(".matcha/infrastructure/matcha.state") as f:
        return dict(json.load(f))


resources = load_state_file()


@app.command("url")
def experiment_tracker_url() -> None:
    """Prints the URL for the experiment tracker provisioned."""
    print(resources.get("mlflow_tracking_url"))


@app.command("username")
def experiment_tracker_username() -> None:
    """Prints the login username for the experiment tracker provisioned."""
    print(resources.get("mlflow_tracking_username"))


@app.command("password")
def experiment_tracker_password() -> None:
    """Prints the login password for the experiment tracker provisioned."""
    print(resources.get("mlflow_tracking_url_password"))


@app.callback(invoke_without_command=True)
def default_callback(context: typer.Context) -> None:
    """Return all the resources if no subcommand is passed.

    Args:
        context (typer.Context): data about the current execution
    """
    if context.invoked_subcommand is None:
        print(
            f"The provisioned experiment-tracker URL: {resources.get('mlflow_tracking_url')}"
        )
        print(
            f"The login username for the experiment-tracker provisioned: {resources.get('mlflow_tracking_username')}"
        )
        print(
            f"The login password for the experiment-tracker provisioned: {resources.get('mlflow_tracking_url_password')}"
        )
