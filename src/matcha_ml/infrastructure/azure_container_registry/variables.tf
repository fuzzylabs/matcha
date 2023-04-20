variable "prefix" {
  description = "A prefix used for all resources"
  type        = string
}

variable "resource_group_name" {
  description = "The resource group name which is used to create the resource group"
  type        = string
}

variable "location" {
  description = "The Azure region in which this resources should be created."
  type        = string
}

variable "aks_object_id" {
  description = "Object id for aks cluster"
  type        = string
}
