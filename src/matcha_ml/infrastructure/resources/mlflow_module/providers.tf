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
