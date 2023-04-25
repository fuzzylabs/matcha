"""Subcommands of resource group."""
import typer

from matcha_ml.cli.ui.print_messages import print_resource_output
from matcha_ml.cli.ui.resource_message_builders import build_resource_output
from matcha_ml.services.matcha_state import MatchaStateService

app = typer.Typer()

matcha_state_service = MatchaStateService()


@app.command("name")
def resource_group_name(
    output: str = typer.Option(
        default=None,
    )
) -> None:
    """Prints the URL for the experiment tracker provisioned."""
    resources = matcha_state_service.fetch_resources_from_state_file(
        ["resource_group_name"]
    )
    resource_output = build_resource_output(resources=resources, output_format=output)
    print_resource_output(resource_output, output_format=output)


@app.callback(invoke_without_command=True)
def default_callback(
    context: typer.Context,
    output: str = typer.Option(
        default=None,
    ),
) -> None:
    """Return all the resources if no subcommand is passed.

    Args:
        context (typer.Context): data about the current execution
        output (typer.Option): the format of the output specified by the user.
    """
    if context.invoked_subcommand is None:
        resource_component_names = [
            "resource_group_name",
        ]
        resources = matcha_state_service.fetch_resources_from_state_file(
            resource_component_names
        )
        resource_output = build_resource_output(
            resources=resources, output_format=output
        )
        print_resource_output(resource_output, output_format=output)
