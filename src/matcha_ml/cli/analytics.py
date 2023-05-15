"""Matcha CLI for opting out of analytics."""
import typer

# create a typer app to group all analytics subcommands
app = typer.Typer()


@app.command()
def opt_out():
    ...
