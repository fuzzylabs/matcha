variable "prefix" {
  description = "A prefix used for all resources"
  default     = "matchatest"
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

variable "mlflow_username" {
  type        = string
  description = "Usernmame to set to access mlflow server"
}

variable "mlflow_password" {
  type        = string
  description = "Password to set to access mlflow server"
  sensitive   = true
}
