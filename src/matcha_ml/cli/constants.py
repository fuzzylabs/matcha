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
    "Matcha originated in China during the Tang Dynasty (618-907 AD) but became popular in Japan during the 12th century. ",
    "Matcha is made from shade-grown tea leaves. The leaves are covered for several weeks before harvest to increase chlorophyll content and develop a rich green color.",
    "Matcha is maintained by Fuzzy Labs",
    "Everything being provisioned is fully open source",
]
