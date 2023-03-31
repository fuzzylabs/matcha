# variables are values that should be supplied 
# by the calling module

# seldon variables
variable "seldon_name" {}
variable "seldon_namespace" {}

variable "resource_group_name" {
  description = "The resource group name which is used to create the resource group"
}

variable "location" {
  description = "The Azure Region in which this resources should be created."
}

# aks cluster variables
variable "aks_cluster_name" {
  type        = string
  description = "Name of the aks cluster"
}

variable "k8_host" {
  description = "Name of the aks host name"
}

variable "k8_client_certificate" {
  description = "aks client certifacte"
  sensitive   = true
}

variable "k8_client_key" {
  description = "aks client key"
}

variable "k8_cluster_ca_certificate" {
  description = "aks client ca certificate"
  sensitive   = true
}
