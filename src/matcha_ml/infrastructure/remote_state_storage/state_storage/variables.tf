variable "resource_group_name" {
  description = "The resource group name which is used to create the resource group"
  type        = string
}

variable "location" {
  description = "The Azure Region in which the remote state storage should be created."
  type        = string
}

variable "prefix" {
  description = "The prefix which should be used for naming storage account ({prefix}statestacc) and container ({prefix}statestore"
  type        = string
}
