variable "prefix" {
  description = "A prefix used for all resources"
  default     = "cattest"
}

variable "location" {
  description = "The Azure Region in which all resources should be provisioned"
}


variable "zenserver_username" {
  description = "Username for ZenServer"
  default     = "default"
}

variable "zenserver_password" {
  description = "Password for ZenServer"
  sensitive   = true
}
