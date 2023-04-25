import json

import typer

app = typer.Typer()


def load_state_file() -> dict:
    with open(".matcha/infrastructure/matcha.state") as f:
        return f.read()


resources = load_state_file()


@app.command("url")
def experiment_tracker_url():
    print(json.loads(resources).get("mlflow_tracking_url"))


@app.command("username")
def experiment_tracker_url():
    print(json.loads(resources).get("mlflow_tracking_username"))


@app.command("password")
def experiment_tracker_url():
    print(json.loads(resources).get("mlflow_tracking_url_password"))
