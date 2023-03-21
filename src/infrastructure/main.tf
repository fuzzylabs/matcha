provider "azurerm" {
  features {}
}

module "resource_group" {
  source = "./resource_group"

  prefix = var.prefix
  location = var.location
}

module "aks" {
  source = "./aks"

  prefix = var.prefix
  location = var.location
  resource_group_name = module.resource_group.name
}
