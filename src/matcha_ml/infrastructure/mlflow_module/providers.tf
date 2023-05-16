# Derived from ZenML's stack recipes; source: https://github.com/zenml-io/mlops-stacks/blob/8eb06596bf836d3a3dd2634fbc7f2b5687421811/aws-minimal/mlflow-module/providers.tf

# defining the providers required by the mlflow module
terraform {
  required_providers {
    htpasswd = {
      source  = "loafoe/htpasswd"
      version = "1.0.4"
    }
  }
  required_version = ">= 0.14.8"
}
