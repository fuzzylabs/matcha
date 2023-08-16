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
