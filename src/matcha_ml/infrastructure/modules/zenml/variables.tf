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

variable "zenmlserver_version" {
  description = "The tag to use for the zenmlserver docker image."
  default     = "latest"
  type        = string
}
