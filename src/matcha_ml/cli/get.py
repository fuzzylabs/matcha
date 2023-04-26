"""Get command CLI."""
import typer

from matcha_ml.cli.resources import experiment_tracker, resource_group
from matcha_ml.cli.ui.print_messages import print_resource_output
from matcha_ml.cli.ui.resource_message_builders import build_resource_output
from matcha_ml.services.matcha_state import MatchaStateService

app = typer.Typer()

# Apps for each command
app.add_typer(
    experiment_tracker.app,
    name="experiment-tracker",
    help="The experiment-tracker command. Default: prints all information of the experiment tracker provisioned.",
)
app.add_typer(
    resource_group.app,
    name="resource-group",
    help="The resource-group command. Default: prints all information of the resource group provisioned.",
)


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
    # if not check_current_deployment_exists():
    #     print_error("Error, no resources are currently provisioned.")
    #     raise typer.Exit()
    if context.invoked_subcommand is None:
        matcha_state_service = MatchaStateService()
        resources = matcha_state_service.fetch_resources_from_state_file()
        resource_output = build_resource_output(
            resources=resources, output_format=output
        )
        print_resource_output(resource_output, output_format=output)
