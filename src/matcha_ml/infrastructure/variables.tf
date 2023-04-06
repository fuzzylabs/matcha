variable "prefix" {
  description = "A prefix used for all resources"
  default     = "matcha"
}

variable "location" {
  description = "The Azure Region in which all resources should be provisioned"
}

variable "username" {
  description = "Username for ZenServer"
  default     = "default"
}

variable "password" {
  description = "Password for ZenServer"
  sensitive   = true
}

# seldon variables
variable "seldon_name" {
  default = "seldon"
}

variable "seldon_namespace" {
  default = "seldon-system"

}
