variable "prefix" {
  description = "A prefix used for all resources"
  default     = "matcha"
}

variable "location" {
  description = "The Azure Region in which all resources should be provisioned"
}

variable "mysql_username" {
  description = "Username to connect to Azure MySQL server"
}

variable "mysql_password" {
  description = "Password to connect to Azure MySQL server"
  sensitive   = true
}
