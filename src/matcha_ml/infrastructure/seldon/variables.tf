# variables are values that should be supplied 
# by the calling module

# seldon variables
variable "seldon_name" {
  description = "Seldon Helm deployment name"
  type = string
}

variable "seldon_namespace" {
  description = "Seldon system namespace"
  type = string
}
