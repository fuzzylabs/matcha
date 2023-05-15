provider "helm" {
  kubernetes {
    host = module.aks.host

    client_certificate     = base64decode(module.aks.client_certificate)
    client_key             = base64decode(module.aks.client_key)
    cluster_ca_certificate = base64decode(module.aks.cluster_ca_certificate)
    config_path            = local.kubectl_config_path
  }
}
