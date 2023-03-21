variable "resource_group_name" {
  description = "The resource group name which is used to create the resource group"
}

variable "location" {
  description = "The Azure Region in which this resources should be created."
}

variable "mysql_server_name" {
  description = "Name of Azure MySQL server"
}

variable "mysql_database_name" {
  description = "Name of database to be created inside Azure MySQL server"
}

variable "mysql_username" {
  description = "Username to connect to Azure MySQL server"
}

variable "mysql_password" {
  description = "Password to connect to Azure MySQL server"
  sensitive   = true
}
