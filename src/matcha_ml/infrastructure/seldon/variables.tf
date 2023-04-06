# variables are values that should be supplied 
# by the calling module

# seldon variables
variable "seldon_name" {
  type = string
  description = "Seldon Helm deployment name"
}

variable "seldon_namespace" {
  type = string
  description = "Seldon system namespace"
}
