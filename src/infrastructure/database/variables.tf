variable "resource_group_name" {
  description = "The resource group name which is used to create the resource group"
}

variable "location" {
  description = "The Azure Region in which this resources should be created."
}

variable "prefix" {
  description = "The prefix which should be used for naming database ({prefix}db) and server ({prefix}server)"
}
variable "mysql_username" {
  description = "Username to connect to Azure MySQL server"
}

variable "mysql_password" {
  description = "Password to connect to Azure MySQL server"
  sensitive   = true
}
