variable "prefix" {
  type        = string
  description = "Prefix to be used for all resources in this module"
}

variable "location" {
  type        = string
  description = "The location/region where the Kubernetes cluster will be created"
}

variable "resource_group_name" {
  type        = string
  description = "The name of the resource group to create the Kubernetes cluster in"
}
