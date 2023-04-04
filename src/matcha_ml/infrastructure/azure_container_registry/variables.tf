variable "prefix" {
  description = "A prefix used for all resources"
}

variable "resource_group_name" {
  description = "The resource group name which is used to create the resource group"
}

variable "location" {
  description = "The Azure Region in which this resources should be created."
}

variable "aks_object_id" {
  description = "Object id for aks cluster"
}
