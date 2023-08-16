variable "prefix" {
  description = "A prefix used for all resources"
  type        = string
  default     = "christest"
}

variable "location" {
  description = "The Azure Region in which all resources should be provisioned"
  type        = string
  default     = "eastus"
}
