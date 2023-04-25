import json

import typer

app = typer.Typer()


def load_state_file() -> dict:
    with open(".matcha/infrastructure/matcha.state") as f:
        return json.load(f)


resources = load_state_file()


@app.command("url")
def experiment_tracker_url():
    print(resources.get("mlflow_tracking_url"))


@app.command("username")
def experiment_tracker_url():
    print(resources.get("mlflow_tracking_username"))


@app.command("password")
def experiment_tracker_url():
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
