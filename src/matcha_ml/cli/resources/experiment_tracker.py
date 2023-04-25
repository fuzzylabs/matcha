"""Subcommands of experiment tracker."""
import typer

from matcha_ml.cli.ui.print_messages import print_resource_output
from matcha_ml.cli.ui.resource_message_builders import build_resource_output
from matcha_ml.services.matcha_state import MatchaStateService

app = typer.Typer()

matcha_state_service = MatchaStateService()


@app.command("url")
def experiment_tracker_url(
    output: str = typer.Option(
        default=None,
        help="The format of your output, e.g., 'json', 'yaml'",
    )
) -> None:
    """Prints the URL for the experiment tracker provisioned."""
    resources = matcha_state_service.fetch_resources_from_state_file(
        ["mlflow_tracking_url"]
    )
    resource_output = build_resource_output(resources=resources, output_format=output)
    print_resource_output(resource_output, output_format=output)


@app.command("username")
def experiment_tracker_username(
    output: str = typer.Option(
        default=None,
        help="The format of your output, e.g., 'json', 'yaml'",
    )
) -> None:
    """Prints the login username for the experiment tracker provisioned."""
    resources = matcha_state_service.fetch_resources_from_state_file(
        ["mlflow_tracking_username"]
    )
    resource_output = build_resource_output(resources=resources, output_format=output)
    print_resource_output(resource_output, output_format=output)


@app.command("password")
def experiment_tracker_password(
    output: str = typer.Option(
        default=None,
        help="The format of your output, e.g., 'json', 'yaml'",
    )
) -> None:
    """Prints the login password for the experiment tracker provisioned."""
    resources = matcha_state_service.fetch_resources_from_state_file(
        ["mlflow_tracking_url_password"]
    )
    resource_output = build_resource_output(resources=resources, output_format=output)
    print_resource_output(resource_output, output_format=output)


@app.callback(invoke_without_command=True)
def default_callback(
    context: typer.Context,
    output: str = typer.Option(
        default=None,
        help="The format of your output, e.g., 'json', 'yaml'",
    ),
) -> None:
    """Return all the resources if no subcommand is passed.

    Args:
        context (typer.Context): data about the current execution
        output (typer.Option): the format of the output specified by the user.
    """
    if context.invoked_subcommand is None:
        resource_component_names = [
            "mlflow_tracking_url",
            "mlflow_tracking_username",
            "mlflow_tracking_url_password",
        ]
        resources = matcha_state_service.fetch_resources_from_state_file(
            resource_component_names
        )
        resource_output = build_resource_output(
            resources=resources, output_format=output
        )
        print_resource_output(resource_output, output_format=output)
