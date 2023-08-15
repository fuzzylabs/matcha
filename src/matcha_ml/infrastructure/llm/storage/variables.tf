variable "resource_group_name" {
  description = "The resource group name which is used to create the resource group"
  type        = string
}

variable "prefix" {
  description = "The prefix which should be used for naming storage account ({prefix}storageacc) and container ({prefix}storagecontainer)"
  type        = string
}

variable "location" {
  description = "The Azure Region in which this resources should be created."
  type        = string
}
