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

module "acr" {
  source = "./azure_container_registry"

  prefix              = var.prefix
  resource_group_name = module.resource_group.name
  location            = var.location
  aks_object_id       = module.aks.aks_object_id
}

module "mlflow" {
  source = "./mlflow_module"

  depends_on = [null_resource.configure-local-kubectl]

  # storage variables
  storage_account_name      = module.storage.storage_account_name
  storage_container_name    = module.storage.storage_container_name
  artifact_Azure_Access_Key = module.storage.primary_access_key

}


module "zenserver" {
  source = "./zen_server"

  depends_on = [null_resource.configure-local-kubectl]

  # resource group variables
  resource_group_name = module.resource_group.name
  location            = var.location

  # ZenServer credentials
  username = var.zenserver_username
  password = var.zenserver_password

}
