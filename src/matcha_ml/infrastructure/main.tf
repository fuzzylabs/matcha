provider "azurerm" {
  features {}
}

module "resource_group" {
  source = "./resource_group"

  prefix   = var.prefix
  location = var.location
}

module "storage" {
  source = "./storage"

  resource_group_name = module.resource_group.name
  prefix              = var.prefix
  location            = var.location
}

module "aks" {
  source = "./aks"

  prefix              = var.prefix
  location            = var.location
  resource_group_name = module.resource_group.name
}

module "mlflow" {
  source = "./mlflow-module"

  # resource group variables
  resource_group_name = module.resource_group.name
  location            = var.location

  # aks variables
  aks_cluster_name          = module.aks.aks_cluster_name
  k8_host                   = module.aks.host
  k8_client_certificate     = module.aks.client_certificate
  k8_client_key             = module.aks.client_key
  k8_cluster_ca_certificate = module.aks.cluster_ca_certificate

  # storage variables
  storage_account_name      = module.storage.storage_account_name
  storage_container_name    = module.storage.storage_container_name
  artifact_Azure_Access_Key = module.storage.primary_access_key

}

module "seldon" {
  source = "./seldon"

  # details about the seldon deployment
  seldon_name      = var.seldon_name
  seldon_namespace = var.seldon_namespace

  # resource group variables
  resource_group_name = module.resource_group.name
  location            = var.location

  # aks variables
  aks_cluster_name          = module.aks.aks_cluster_name
  k8_host                   = module.aks.host
  k8_client_certificate     = module.aks.client_certificate
  k8_client_key             = module.aks.client_key
  k8_cluster_ca_certificate = module.aks.cluster_ca_certificate
}

resource "kubernetes_namespace" "seldon-workloads" {
  metadata {
    name = "matcha-seldon-workloads"
  }
}


# add role to allow kubeflow to access kserve
resource "kubernetes_cluster_role_v1" "seldon" {
  metadata {
    name = "seldon-permission"
    labels = {
      app = "matcha"
    }
  }

  rule {
    api_groups = ["*"]
    resources  = ["*"]
    verbs      = ["*"]
  }

  depends_on = [
    module.seldon,
  ]
}

# assign role to kubeflow pipeline runner
resource "kubernetes_cluster_role_binding_v1" "binding" {
  metadata {
    name = "seldon-permission-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role_v1.seldon.metadata[0].name
  }
  subject {
    kind = "User"
    name = "system:serviceaccount:kubeflow:pipeline-runner"
  }
}
