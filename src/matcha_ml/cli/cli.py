"""Matcha CLI."""
from typing import Optional

import typer

from matcha_ml import __version__
from matcha_ml.cli import provision

app = typer.Typer(no_args_is_help=True)

# Create a group for all subcommands
app.add_typer(provision.app, name="provision", help="Provision cloud resources.")


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
    """
    pass


if __name__ == "__main__":
    app()
