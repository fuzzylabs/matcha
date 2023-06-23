provider "azurerm" {
  features {}
}

module "resource_group" {
  source = "./resource_group"

  prefix   = var.prefix
  location = var.location
}

module "state_storage" {
  source = "./state_storage"

  # otherwise the module will be created before resource group is ready
  depends_on = [module.resource_group]

  resource_group_name = module.resource_group.name
  location            = var.location
  prefix              = var.prefix
}
