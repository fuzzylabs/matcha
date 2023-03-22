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

module "database" {
  source = "./database"

  resource_group_name = module.resource_group.name
  prefix              = var.prefix
  location            = var.location
  mysql_username      = var.mysql_username
  mysql_password      = var.mysql_password
}


module "aks" {
  source = "./aks"

  prefix              = var.prefix
  location            = var.location
  resource_group_name = module.resource_group.name
}

module "mlflow-module" {
  source = "./mlflow-module"

  # resource group variables
  resource_group_name = module.resource_group.name
  location            = var.location

  # aks variables
  aks_cluster_name          = module.aks.aks_cluster_name
  k8_host                   = module.aks.host
  k8_client_certificate     = module.aks.client_certificate
  k8_client_key             = module.aks.client_key
  k8_cluster_ca_certificate = module.aks.cluster_ca_certificate

  # mlflow variables
  mlflow_username = var.mlflow_username
  mlflow_password = var.mlflow_password

  # storage variables
  storage_account_name      = module.storage.storage_account_name
  storage_container_name    = module.storage.storage_container_name
  artifact_Azure_Access_Key = module.storage.primary_access_key

  # database variables
  backend_Azure_Mysql_Host     = module.database.mysql_db_host
  backend_Azure_Mysql_Port     = module.database.mysql_server_port
  backend_Azure_Mysql_User     = module.database.mysql_server_username
  backend_Azure_Mysql_Password = module.database.mysql_server_password
  mlflow_mysql_database_name   = module.database.mysql_database_name
}
