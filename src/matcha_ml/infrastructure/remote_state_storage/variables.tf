variable "location" {
  description = "The Azure Region in which this resources should be created."
  type        = string
}

variable "prefix" {
  description = "A prefix used for the resource group name"
  type        = string
  default     = "matcha"
}
