# a default (non-aliased) provider configuration for "kubernetes"
provider "kubernetes" {
  host = var.k8_host

  client_certificate     = base64decode(var.k8_client_certificate)
  client_key             = base64decode(var.k8_client_key)
  cluster_ca_certificate = base64decode(var.k8_cluster_ca_certificate)
}

provider "kubectl" {
  host = var.k8_host

  client_certificate     = base64decode(var.k8_client_certificate)
  client_key             = base64decode(var.k8_client_key)
  cluster_ca_certificate = base64decode(var.k8_cluster_ca_certificate)
}
