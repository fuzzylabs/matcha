"""Matcha CLI."""
from typing import Optional

import typer

from matcha_ml import __version__
from matcha_ml.cli import run
from matcha_ml.cli._validation import prefix_typer_callback, region_typer_callback
from matcha_ml.cli.destroy import destroy_resources
from matcha_ml.cli.provision import provision_resources
from matcha_ml.cli.ui.print_messages import print_status

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)

# Create a group for all subcommands
app.add_typer(
    run.app,
    name="run",
    help="The run command. Default: finds and executes the pipelines run.py in the current directory if no command is passed.",
)


@app.command()
def provision(
    location: str = typer.Option(
        None,
        prompt="What region should your resources be provisioned in (e.g., 'ukwest')?",
        callback=region_typer_callback,
        help="The region where your resources will be provisioned, e.g., 'ukwest'",
    ),
    prefix: str = typer.Option(
        prompt="Your resources need a name (a alphanumerical prefix; 3-24 character limit), what should matcha call them?",
        callback=prefix_typer_callback,
        default="matcha",
        help="A unique prefix for your resources.",
    ),
    password: str = typer.Option(
        prompt="Please provide a password for ZenServer.",
        confirmation_prompt=True,
        hide_input=True,
        help="Password for Zenserver",
        default="default",
    ),
    verbose: Optional[bool] = typer.Option(
        False, help="Get more detailed information from matcha provision!"
    ),
) -> None:
    """Provision cloud resources with a template."""
    provision_resources(location, prefix, password, verbose)


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
