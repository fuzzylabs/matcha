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
