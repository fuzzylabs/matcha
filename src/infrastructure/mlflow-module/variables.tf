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
  description = "Name of the aks host name"
}

variable "k8_client_certificate" {
  description = "aks client certifacte"
  sensitive   = true
}

variable "k8_client_key" {
  description = "aks client key"
}

variable "k8_cluster_ca_certificate" {
  description = "aks client ca certificate"
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
