variable "prefix" {
  description = "Prefix to be used for all resources in this module"
  type        = string
}

variable "location" {
  description = "The Azure region where the Kubernetes cluster will be created"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group to create the Kubernetes cluster in"
  type        = string
}
