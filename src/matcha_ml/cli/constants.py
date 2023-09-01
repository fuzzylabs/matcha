"""Constants for use within the Matcha CLI."""
RESOURCE_MSG_CORE = [
    ("Azure Kubernetes Service (AKS)", "A kubernetes cluster"),
    (
        "Azure Container Registry",
        "A container registry for storing docker images",
    ),
]

RESOURCE_MSG_MODULES = {
    "deployer": (
        "Seldon Core",
        "A framework for model deployment on top of a kubernetes cluster",
    ),
    "orchestrator": (
        "ZenServer",
        "A zenml server required for remote orchestration and a storage container",
    ),
    "data_version_control": (
        "Data Version Control",
        "A storage container to hold data versions",
    ),
    "experiment_tracker": (
        "MLflow",
        "An experiment tracker backed by a storage container",
    ),
    "vector_database": ("Chroma", "A vector database"),
}

STATE_RESOURCE_MSG = [
    ("Azure Resource Group", "The resource group containing the provisioned resources"),
    ("Matcha State Container", "A storage container for tracking matcha state"),
]

INFRA_FACTS = [
    "Did you know that Matcha tea was created by accident?",
    "The brewing temperature of the water affects the taste of Matcha",
    "Samurai's drank Matcha before battles",
    "Matcha is provisioning Kubernetes which orchestrates tools",
    "Seldon Core is used for model deployment",
    "MLflow is used as an experiment tracker",
    "Matcha is maintained by Fuzzy Labs",
    "Everything being provisioned is fully open source",
]
