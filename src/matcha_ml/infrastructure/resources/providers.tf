# defining the providers for the all module
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">=3.16.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "3.1.0"
    }

    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0.1"
    }

    local = {
      source  = "hashicorp/local"
      version = "2.1.0"
    }

    null = {
      source  = "hashicorp/null"
      version = "3.2.1"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.11.0"
    }

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
