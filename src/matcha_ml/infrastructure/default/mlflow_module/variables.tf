# artifact storage variables
variable "artifact_proxied_access" {
  description = "Boolean to indicate if we are using proxied artifact storage"
  type        = bool
  default     = false
}

variable "storage_account_name" {
  description = "Name of Azure Storage Container already created inside Azure Blob Storage"
  type        = string
}

variable "storage_container_name" {
  description = "Name of container to create inside Azure Storage Account to store artifacts"
  type        = string
}

variable "artifact_azure" {
  description = "Boolean to indicate if we are using Azure Blob Storage as storage for MLFlow"
  type        = bool
  default     = true
}


variable "artifact_azure_access_key" {
  description = "Access Key for Azure Blob Storage"
  type        = string
  default     = ""
}
