# resource group variables
variable "resource_group_name" {
  description = "The resource group name which is used to create the resource group"
}

variable "location" {
  description = "The Azure Region in which this resources should be created."
}

# aks cluster variables
variable "aks_cluster_name" {
  type        = string
  description = "Name of the aks cluster"
}

variable "k8_host" {
  description = "Host name"
}

variable "k8_client_certificate" {
  description = "k8 client certifacte"
}

variable "k8_client_key" {
  description = "k8 client key"

}

variable "k8_cluster_ca_certificate" {
  description = "k8 client ca certificate"

}

# mlflow namespace
variable "mlflow_namespace" {
  type    = string
  default = "mlflow"
}

# mlflow credentials
variable "mlflow_username" {
  type        = string
  description = "Usernmame to set to access mlflow server"
}

variable "mlflow_password" {
  type        = string
  description = "Password to set to access mlflow server"
  sensitive   = true
}


# artifact storage variables
variable "artifact_Proxied_Access" {
  type    = bool
  default = false
}

variable "storage_account_name" {
  type        = string
  description = "Name of Azure Storage Container already created inside Azure Blob Storage"
}

variable "storage_container_name" {
  type        = string
  description = "Name of container to create inside Azure Storage Account to store artifacts"
}

variable "artifact_Azure" {
  type        = bool
  default     = true
  description = "Boolean to indicate if we are using Azure Blob Storage as storage for MLFlow"
}

variable "artifact_Azure_Access_Key" {
  type        = string
  default     = ""
  description = "Access Key for Azure Blob Storage"
}

# backend store variables
variable "backend_Azure_Mysql_DatabaseMigration" {
  type        = bool
  default     = true
  description = "Specifies if you want to run database migration"
}

variable "backend_Azure_Mysql_Enabled" {
  type        = bool
  default     = true
  description = "Boolean to indicate if we are using Azure MySQL Database as backend for MLFlow"
}

variable "backend_Azure_Mysql_Host" {
  type        = string
  description = "Host name to access Azure MySQL Database (dbname.mysql.database.azure.com)"
}

variable "backend_Azure_Mysql_Port" {
  description = "Port to access Azure MySQL Database"
  default     = 3306
}

variable "backend_Azure_Mysql_User" {
  description = "Username to access Azure MySQL Database"
}

variable "backend_Azure_Mysql_Password" {
  description = "Password to access Azure MySQL Database"
}

variable "mlflow_mysql_database_name" {
  type        = string
  description = "Name of database to create inside Azure MySQL server to store mlflow runs"
}
