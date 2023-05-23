provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
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

  depends_on = [null_resource.configure_local_kubectl]

  # storage variables
  storage_account_name      = module.storage.storage_account_name
  storage_container_name    = module.storage.storage_container_name
  artifact_azure_access_key = module.storage.primary_access_key

}


module "zenserver" {
  source = "./zen_server"

  depends_on = [null_resource.configure_local_kubectl]

  # resource group variables
  resource_group_name = module.resource_group.name
  location            = var.location
  prefix              = var.prefix

  # ZenServer credentials
  username = var.username
  password = var.password
}


module "seldon" {
  source = "./seldon"

  depends_on = [null_resource.configure_local_kubectl]

  # details about the seldon deployment
  seldon_name      = var.seldon_name
  seldon_namespace = var.seldon_namespace

}
