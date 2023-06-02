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
