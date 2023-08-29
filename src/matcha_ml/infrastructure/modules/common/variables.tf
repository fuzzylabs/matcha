variable "prefix" {
  description = "A prefix used for all resources"
  type        = string
}

variable "location" {
  description = "The Azure Region in which all resources should be provisioned"
  type        = string
}

variable "vm_size" {
  description = "The Azure VM size to use."
  type        = string
  default     = "Standard_DS3_v2"
}
