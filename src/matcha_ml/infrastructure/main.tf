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
  source = "mlflow"

  depends_on = [null_resource.configure-local-kubectl]

  # storage variables
  storage_account_name      = module.storage.storage_account_name
  storage_container_name    = module.storage.storage_container_name
  artifact_Azure_Access_Key = module.storage.primary_access_key

}

module "seldon" {
  source = "./seldon"

  depends_on = [null_resource.configure-local-kubectl]

  # details about the seldon deployment
  seldon_name      = var.seldon_name
  seldon_namespace = var.seldon_namespace
}
