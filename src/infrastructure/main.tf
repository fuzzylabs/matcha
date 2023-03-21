provider "azurerm" {
  features {}
}

module "resource_group" {
  source = "./resource_group"

  prefix   = var.prefix
  location = var.location
}

module "aks" {
  source = "./aks"

  prefix              = var.prefix
  location            = var.location
  resource_group_name = module.resource_group.name
}

module "storage" {
  source = "./storage"

  prefix              = var.prefix
  location            = var.location
  resource_group_name = module.resource_group.name
}

module "database" {
  source = "./database"

  location            = var.location
  resource_group_name = module.resource_group.name
  mysql_database_name = var.mysql_database_name
  mysql_server_name   = var.mysql_server_name
  mysql_password      = var.mysql_password
  mysql_username      = var.mysql_username
}
