"""Matcha CLI."""
from typing import Optional

import typer

from matcha_ml import __version__
from matcha_ml.cli import run
from matcha_ml.cli.provision import provision_resources

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)

# Create a group for all subcommands
app.add_typer(
    run.app,
    name="run",
    help="Run command. Executes run.py in the current directory by default if no command is passed.",
)


@app.command()
def provision(
    location: Optional[str] = typer.Option(
        None, help="Azure location in which all resources will be provisioned."
    ),
    prefix: Optional[str] = typer.Option(None, help="Prefix used for all resources."),
) -> None:
    """Provision cloud resources with a template.

    Args:
        location (str, optional): Azure location in which all resources will be provisioned.
        prefix (str, optional): Prefix used for all resources.
    """
    provision_resources(location, prefix)


def version_callback(value: bool) -> None:
    """Print version for matcha cli.

    Args:
        value (bool): Whether to print version based on if callback is triggered.

    Raises:
        Exit: Exit after printing version.
    """
    if value:
        typer.secho(f"Matcha version: {__version__}", bold=True)
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

    Args:
        version (bool, optional): matcha version flag
    """
    pass


if __name__ == "__main__":
    app()
