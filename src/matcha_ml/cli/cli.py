"""Matcha CLI."""
from typing import Optional

import typer

from matcha_ml import __version__
from matcha_ml.cli import run
from matcha_ml.cli.provision import provision_resources

app = typer.Typer(no_args_is_help=True)


@app.command()
def provision(
    template: Optional[str] = typer.Option(
        None, help="Template to use for provisioning."
    )
) -> None:
    """Provision cloud resources with a template.

    Args:
        template (str, optional): Path to template.
                                Defaults to typer.Option(..., help="Template to use for provisioning.").
    """
    provision_resources(template)


# Create a group for all subcommands
app.add_typer(run.app, name="run", help="Run command.")


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
