"""Provision CLI."""
from typing import Optional

import typer

# create a typer app to group all provision subcommands
app = typer.Typer()


@app.callback()
def provision(
    template: Optional[str] = typer.Option(
        ..., help="Template to use for provisioning."
    )
) -> None:
    """Provision cloud resources with a template.

    Args:
        template (str, optional): Path to template.
                                Defaults to typer.Option(..., help="Template to use for provisioning.").
    """
    pass
