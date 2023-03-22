"""Run CLI for matcha."""
from typing import Optional

import typer

from rich.console import Console
import runpy

stdout_console = Console()
err_console = Console(stderr=True)

# create a typer app to group all run subcommands
app = typer.Typer()


@app.command()
def train() -> None:
    """Run train subcommand."""
    pass


@app.callback(invoke_without_command=True)
def default_callback(context: typer.Context) -> None:
    """Run run.py if no subcommand is passed."""
    if context.invoked_subcommand is None:
        try:
            stdout_console.print("No commands are passed, running run.py by default.")
            runpy.run_path('run.py', run_name="__main__")
            
        except FileNotFoundError:
            err_console.print("FileNotFoundError: No 'run.py' file found in this directory.", style="blink")
