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

module "zenml_storage" {
  source = "./zenml_storage"

  prefix              = var.prefix
  resource_group_name = module.resource_group.name
  location            = var.location
  aks_principal_id    = module.aks.aks_principal_id
}

module "aks" {
  source = "./aks"

  prefix              = var.prefix
  location            = var.location
  resource_group_name = module.resource_group.name
}

module "mlflow" {
  source = "./mlflow_module"

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


module "zenserver" {
  source = "./zen_server"

  # resource group variables
  resource_group_name = module.resource_group.name
  location            = var.location

  # ZenServer credentials
  username = var.zenserver_username
  password = var.zenserver_password

}
