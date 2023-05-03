"""Matcha CLI."""
from typing import Optional

import typer

from matcha_ml import __version__
from matcha_ml.cli._validation import (
    check_current_deployment_exists,
    prefix_typer_callback,
    region_typer_callback,
)
from matcha_ml.cli.destroy import destroy_resources
from matcha_ml.cli.provision import provision_resources
from matcha_ml.cli.ui.print_messages import (
    hide_sensitive_in_output,
    print_error,
    print_resource_output,
    print_status,
)
from matcha_ml.cli.ui.resource_message_builders import build_resource_output
from matcha_ml.core import core
from matcha_ml.errors import MatchaError, MatchaInputError

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


@app.command()
def provision(
    location: str = typer.Option(
        None,
        prompt="What region should your resources be provisioned in (e.g., 'ukwest')?",
        callback=region_typer_callback,
        help="The region where your resources will be provisioned, e.g., 'ukwest'",
    ),
    prefix: str = typer.Option(
        prompt="Your resources need a name (an alphanumerical prefix; 3-11 character limit), what should matcha call them?",
        callback=prefix_typer_callback,
        default="matcha",
        help="A unique prefix for your resources.",
    ),
    password: str = typer.Option(
        default=None,
        prompt="Set a password for your deployment server",
        confirmation_prompt=True,
        hide_input=True,
        help="A password for the deployment server",
    ),
    verbose: Optional[bool] = typer.Option(
        False, help="Get more detailed information from matcha provision!"
    ),
) -> None:
    """Provision cloud resources with a template."""
    if check_current_deployment_exists():
        print_error(
            "WARNING: A deployment already exists in Azure, if you continue you'll create a orphan resource - use 'matcha destroy' before trying to provision."
        )
    provision_resources(location, prefix, password, verbose)


@app.command(help="Get information for the provisioned resources.")
def get(
    resource_name: Optional[str] = typer.Argument(None),
    property_name: Optional[str] = typer.Argument(None),
    output: str = typer.Option(
        default=None,
        help="The format of your output, e.g., 'json', 'yaml'",
    ),
) -> None:
    """Get information for the provisioned resources.

    Args:
        resource_name (Optional[str]): the name of the resource.
        property_name (Optional[str]): the specific property of the resource to return.
        output (typer.Option): the format of the output specified by the user.

    Raises:
        Exit: Exit if matcha.state file does not exist.
        Exit: Exit if resource type or property does not exist in matcha.state.
    """
    try:
        resources = core.get(resource_name, property_name)
    except MatchaError as e:
        print_error(str(e))
        raise typer.Exit()
    except MatchaInputError as e:
        print_error(str(e))
        raise typer.Exit()

    resources = hide_sensitive_in_output(resources)
    resource_output = build_resource_output(resources=resources, output_format=output)
    print_resource_output(resource_output=resource_output, output_format=output)


@app.command()
def destroy() -> None:
    """Destroy the provisioned cloud resources."""
    destroy_resources()


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

    For more help on how to use matcha, head to https://docs.mlops.wtf
    """
    pass


if __name__ == "__main__":
    app()
