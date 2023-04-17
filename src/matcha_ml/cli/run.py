"""Run CLI for matcha."""
import subprocess
import os

import typer

from matcha_ml.cli.ui.print_messages import print_error, print_status
from matcha_ml.cli.ui.status_message_builders import build_status

# create a typer app to group all run subcommands
app = typer.Typer()


@app.command()
def train() -> None:
    """Run train subcommand."""
    file_path = os.path.join(os.getcwd(), "run.py")
    
    if not os.path.isfile(file_path):
        print_error("Matcha cannot find a 'run.py' file, make sure you are in a directory that has one.")
    else:
        try:
            print_status(
                build_status("Running the training pipeline.")
            )
            subprocess.run(["python3", "run.py", "--train"], check=True)
        except subprocess.CalledProcessError as e:
            print_error(e)


@app.callback(invoke_without_command=True)
def default_callback(context: typer.Context) -> None:
    """Run run.py if no subcommand is passed.

    Args:
        context (typer.Context): data about the current execution
    """
    if context.invoked_subcommand is None:
        file_path = os.path.join(os.getcwd(), "run.py")
    
        if not os.path.isfile(file_path):
            print_error("Matcha cannot find a 'run.py' file, make sure you are in a directory that has one.")
        else:
            try:
                print_status(
                    build_status("No commands are passed, running run.py by default.")
                )
                subprocess.run(["python3", "run.py"], check=True)
            except subprocess.CalledProcessError as e:
                print_error(e)
