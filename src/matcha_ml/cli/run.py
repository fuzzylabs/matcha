"""Run CLI for matcha."""
from typing import Optional

import typer

# create a typer app to group all run subcommands
app = typer.Typer()


@app.command()
def train() -> None:
    """Run train subcommand."""
    pass
