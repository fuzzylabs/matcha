"""Matcha CLI."""
from typing import Optional

import typer

from matcha_ml import __version__
from matcha_ml.cli._validation import (
    prefix_typer_callback,
    region_typer_callback,
)
from matcha_ml.cli.constants import RESOURCE_MSG, STATE_RESOURCE_MSG
from matcha_ml.cli.destroy import destroy_resources
from matcha_ml.cli.provision import provision_resources
from matcha_ml.cli.ui.print_messages import (
    print_error,
    print_resource_output,
    print_status,
)
from matcha_ml.cli.ui.resource_message_builders import (
    build_resource_output,
    hide_sensitive_in_output,
)
from matcha_ml.cli.ui.status_message_builders import build_warning_status
from matcha_ml.core import core
from matcha_ml.errors import MatchaError, MatchaInputError
from matcha_ml.services.analytics_service import AnalyticsEvent, track
from matcha_ml.state import RemoteStateManager

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)
analytics_app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)
app.add_typer(
    analytics_app,
    name="analytics",
    help="Enable or disable the collection of anonymous usage data (enabled by default).",
)


@app.command()
@track(event_name=AnalyticsEvent.PROVISION)
def provision(
    location: str = typer.Option(
        callback=region_typer_callback,
        default="",
        help="The region where your resources will be provisioned, e.g., 'ukwest'",
    ),
    prefix: str = typer.Option(
        callback=prefix_typer_callback,
        default="",
        help="A unique prefix for your resources.",
    ),
    password: str = typer.Option(
        default="",
        help="A password for the deployment server",
    ),
    verbose: Optional[bool] = typer.Option(
        False, help="Get more detailed information from matcha provision!"
    ),
) -> None:
    """Provision cloud resources with a template."""
    provision_resources(location, prefix, password, verbose)


@app.command(help="Get information for the provisioned resources.")
@track(event_name=AnalyticsEvent.GET)
def get(
    resource_name: Optional[str] = typer.Argument(None),
    property_name: Optional[str] = typer.Argument(None),
    output: Optional[str] = typer.Option(
        default=None,
        help="The format of your output, e.g., 'json', 'yaml'.",
    ),
    show_sensitive: Optional[bool] = typer.Option(
        default=False,
        help="Show hidden sensitive value such as passwords.",
    ),
) -> None:
    """Get information for the provisioned resources.

    Args:
        resource_name (Optional[str]): the name of the resource.
        property_name (Optional[str]): the specific property of the resource to return.
        output (Optional[str]): the format of the output specified by the user.
        show_sensitive (Optional[bool]): show hidden sensitive resource values when True. Defaults to False.

    Raises:
        Exit: Exit if matcha remote state has not been provisioned.
        Exit: Exit if matcha.state file does not exist.
        Exit: Exit if resource type or property does not exist in matcha.state.
    """
    try:
        resources = core.get(resource_name, property_name)
    except MatchaInputError as e:
        print_error(str(e))
        raise typer.Exit()
    except MatchaError as e:
        print_error(str(e))
        raise typer.Exit()

    if not show_sensitive:
        resources = hide_sensitive_in_output(resources)

    resource_output = build_resource_output(resources=resources, output_format=output)
    print_resource_output(resource_output=resource_output, output_format=output)


@app.command()
@track(event_name=AnalyticsEvent.DESTROY)
def destroy(
    full: Optional[str] = typer.Argument(
        default=None,
        help="When the full command is specified, the resource group and all its provisioned resources will be destroyed together.",
    ),
) -> None:
    """Destroy the provisioned cloud resources."""
    remote_state_manager = RemoteStateManager()
    if full:
        destroy_resources(resources=STATE_RESOURCE_MSG + RESOURCE_MSG)
        remote_state_manager.deprovision_remote_state()
    else:
        print_status(
            build_warning_status(
                "Warning: a storage container holding Matcha state information will persist. To destroy ALL clound resources, run 'matcha destroy full'."
            )
        )
        destroy_resources(resources=RESOURCE_MSG)


@app.command()
def force_unlock() -> None:
    """Force unlock remote matcha state on Azure."""
    delete = typer.confirm("Are you sure you want to remove the lock forcefully?")
    if not delete:
        raise typer.Exit()
    core.remove_state_lock()


def version_callback(value: bool) -> None:
    """Print version for matcha cli.

    Args:
        value (bool): Whether to print version based on if callback is triggered.

    Raises:
        Exit: Exit after printing version.
    """
    if value:
        print_status(f"Matcha version: {__version__}")
        raise typer.Exit()


@app.callback()
def cli(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Matcha version."
    ),
) -> None:
    """CLI base command for matcha.

    Run 'matcha <command> --help' for more information on a specific command.

    For more help on how to use matcha, head to https://fuzzylabs.github.io/matcha/
    """
    pass


@analytics_app.command()
def opt_out() -> None:
    """Disable the collection of anonymous usage data."""
    print(
        "Data collection has been turned off and no data will be collected - you can turn this back on by running the command: 'matcha analytics opt-in'."
    )
    core.analytics_opt_out()


@analytics_app.command()
def opt_in() -> None:
    """Enable the collection of anonymous usage data (enabled by default)."""
    print(
        "Thank you for enabling data collection, this helps us improve matcha and anonymously understand how people are using the tool."
    )
    core.analytics_opt_in()


if __name__ == "__main__":
    app()
