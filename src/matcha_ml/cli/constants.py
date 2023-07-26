"""Constants for use within the Matcha CLI."""
RESOURCE_MSG = [
    ("Azure Kubernetes Service (AKS)", "A kubernetes cluster"),
    (
        "Two Storage Containers",
        "A storage container for experiment tracking artifacts and a second for model training artifacts",
    ),
    (
        "Seldon Core",
        "A framework for model deployment on top of a kubernetes cluster",
    ),
    (
        "Azure Container Registry",
        "A container registry for storing docker images",
    ),
    ("ZenServer", "A zenml server required for remote orchestration"),
]

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
