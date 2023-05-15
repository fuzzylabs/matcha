provider "azurerm" {
  features {}
}

module "resource_group" {
    source = "./resource_group"
}

module "storage" {
    source = "./storage"

    # otehrwise the module will be created before resource group is ready
    depends_on = [ module.resource_group ]
    

    # location = var.location
}
