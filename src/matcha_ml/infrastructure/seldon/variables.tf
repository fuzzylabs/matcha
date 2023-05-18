# Derived from ZenML's stack recipes; source: https://github.com/zenml-io/mlops-stacks/blob/8eb06596bf836d3a3dd2634fbc7f2b5687421811/aws-minimal/seldon/variables.tf

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
