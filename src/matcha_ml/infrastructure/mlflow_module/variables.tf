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
