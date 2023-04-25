import json

import typer

app = typer.Typer()


@app.command("url")
def experiment_tracker_url(resources: str):
    print(json.loads(resources).get("mlflow_tracking_url"))
