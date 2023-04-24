variable "prefix" {
  description = "A prefix used for all resources"
  type        = string
}

variable "resource_group_name" {
  description = "The resource group name which is used to create the resource group"
  type        = string
}

variable "location" {
  description = "The Azure Region in which this resources should be created."
  type        = string
}

variable "aks_principal_id" {
  description = "Principal id for aks cluster"
  type        = string
}
