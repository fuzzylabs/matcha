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

  resource_group_name = module.resource_group.name
  prefix              = var.prefix
  location            = var.location
}

module "database" {
  source = "./database"

  resource_group_name = module.resource_group.name
  prefix              = var.prefix
  location            = var.location
  mysql_password      = var.mysql_password
  mysql_username      = var.mysql_username
}

module "mlflow" {
  source = "./mlflow"

  resource_group_name           = module.resource_group.name
  location                      = var.location
  aks_cluster_name              = module.aks.aks_cluster_name
  mlflow_username               = var.mlflow_username
  mlflow_password               = var.mlflow_password
  storage_account_name          = module.storage.storage_account_name
  mlflow_storage_container_name = module.storage.storage_container_name
  artifact_Azure_Access_Key     = module.storage.primary_access_key
  backend_Azure_Mysql_Host      = module.database.mysql_db_host
  backend_Azure_Mysql_Port      = module.database.mysql_server_port
  backend_Azure_Mysql_User      = var.mysql_username
  backend_Azure_Mysql_Password  = var.mysql_password
  mlflow_mysql_database_name    = module.database.mysql_database_name
}
