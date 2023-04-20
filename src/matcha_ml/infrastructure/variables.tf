variable "prefix" {
  description = "A prefix used for all resources"
  type        = string
  default     = "matcha"
}

variable "location" {
  description = "The Azure Region in which all resources should be provisioned"
  type        = string
}

variable "username" {
  description = "Username for ZenServer"
  type        = string
  default     = "default"
}

variable "password" {
  description = "Password for ZenServer"
  type        = string
  sensitive   = true
}

# seldon variables
variable "seldon_name" {
  description = "Name of the Seldon deployment"
  type        = string
  default     = "seldon"
}

variable "seldon_namespace" {
  description = "Namespace for Seldon resources"
  type        = string
  default     = "seldon-system"

}
