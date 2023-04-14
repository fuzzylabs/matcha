"""Run CLI for matcha."""
from typing import Optional
import subprocess

import typer

from matcha_ml.cli.ui.print_messages import print_error, print_status
from matcha_ml.cli.ui.status_message_builders import build_status

# create a typer app to group all run subcommands
app = typer.Typer()


@app.command()
def train(context: typer.Context) -> None:
    """Run train subcommand."""
    if context.invoked_subcommand is None:
        try:
            print_status(
                build_status("Running run.py with '--train' argument.")
            )
            subprocess.run(["python3", "run.py", "--train"])

        except FileNotFoundError:
            print_error(
                "FileNotFoundError: No 'run.py' file found in this directory.",
            )


@app.callback(invoke_without_command=True)
def default_callback(context: typer.Context) -> None:
    """Run run.py if no subcommand is passed.

    Args:
        context (typer.Context): data about the current execution
    """
    if context.invoked_subcommand is None:
        try:
            print_status(
                build_status("No commands are passed, running run.py by default.")
            )
            subprocess.run(["python3", "run.py"])

        except FileNotFoundError:
            print_error(
                "FileNotFoundError: No 'run.py' file found in this directory.",
            )