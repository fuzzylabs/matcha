# defining the providers for the zenserver module
terraform {
  required_providers {
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "1.14.0"
    }

    htpasswd = {
      source  = "loafoe/htpasswd"
      version = "1.0.4"
    }
  }

  required_version = ">= 0.14.8"
}
