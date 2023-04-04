variable "prefix" {
  description = "A prefix used for all resources"
  default     = "matcha"
}

variable "location" {
  description = "The Azure Region in which all resources should be provisioned"
}


variable "zenserver_user" {
  description = "Username for ZenServer"
  default     = "default"
}

variable "zenserver_pass" {
  description = "Password for ZenServer"
  sensitive   = true
}
