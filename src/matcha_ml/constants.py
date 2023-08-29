"""General constants file."""
import os

from matcha_ml.config.matcha_config import MatchaConfigComponentProperty

LOCK_FILE_NAME = "matcha.lock"
MATCHA_STATE_PATH = os.path.join(".matcha", "infrastructure", "matcha.state")

STACK_MODULES = {
    "orchestrator": {"zenml": MatchaConfigComponentProperty("orchestrator", "zenml")},
    "experiment_tracker": {
        "mlflow": MatchaConfigComponentProperty("experiment_tracker", "mlflow")
    },
    "data_version_control": {
        "dvc": MatchaConfigComponentProperty("data_version_control", "dvc")
    },
    "vector_database": {
        "chroma": MatchaConfigComponentProperty("vector_database", "chroma")
    },
    "deployer": {"seldon": MatchaConfigComponentProperty("deployer", "seldon")},
}
