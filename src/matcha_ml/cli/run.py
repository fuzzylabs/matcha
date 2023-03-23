"""Run CLI for matcha."""
import runpy
from typing import Optional

import typer
from rich import print
from rich.console import Console

err_console = Console(stderr=True)

# create a typer app to group all run subcommands
app = typer.Typer()


@app.command()
def train() -> None:
    """Run train subcommand."""
    pass


@app.callback(invoke_without_command=True)
def default_callback(context: typer.Context) -> None:
    """Run run.py if no subcommand is passed.

    Args:
        context (typer.Context): data about the current execution
    """
    if context.invoked_subcommand is None:
        try:
            print("No commands are passed, running run.py by default.")
            runpy.run_path("run.py", run_name="__main__")

        except FileNotFoundError:
            err_console.print(
                "FileNotFoundError: No 'run.py' file found in this directory.",
                style="blink",
            )
