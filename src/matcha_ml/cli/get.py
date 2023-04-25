"""Get command CLI."""
import typer

from matcha_ml.cli import experiment_tracker
from matcha_ml.cli.ui.print_messages import print_resource_output
from matcha_ml.cli.ui.resource_message_builders import build_resource_output
from matcha_ml.services.matcha_state import MatchaStateService

app = typer.Typer()
app.add_typer(
    experiment_tracker.app,
    name="experiment-tracker",
    help="The get command. Default: prints all information about the current provisioned resources.",
)


matcha_state_service = MatchaStateService()


@app.command(name="resource-group")
def resource_group(
    output: str = typer.Option(
        default=None,
    )
) -> None:
    """Gets the resource group information."""
    resource_component_names = ["resource_group_name"]
    resources = matcha_state_service.fetch_resources_from_state_file(
        resource_component_names
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
    # if not check_current_deployment_exists():
    #     print_error("Error, no resources are currently provisioned.")
    #     raise typer.Exit()
    if context.invoked_subcommand is None:
        resources = matcha_state_service.fetch_resources_from_state_file()
        resource_output = build_resource_output(
            resources=resources, output_format=output
        )
        print_resource_output(resource_output, output_format=output)
