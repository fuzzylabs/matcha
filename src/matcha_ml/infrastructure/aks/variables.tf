variable "prefix" {
  description = "A prefix used for all resources"
}

variable "location" {
  description = "The Azure Region in which k8s cluster should be provisioned"
}

variable "resource_group_name" {
  description = "The Azure resource group name to provision k8s cluster in"
}
