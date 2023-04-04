output "id" {
  value = azurerm_kubernetes_cluster.matcha_kubernetes_cluster.id
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.matcha_kubernetes_cluster.kube_config_raw
  sensitive = true
}

output "client_key" {
  value = azurerm_kubernetes_cluster.matcha_kubernetes_cluster.kube_config.0.client_key
}

output "client_certificate" {
  value     = azurerm_kubernetes_cluster.matcha_kubernetes_cluster.kube_config.0.client_certificate
  sensitive = true
}

output "cluster_ca_certificate" {
  value = azurerm_kubernetes_cluster.matcha_kubernetes_cluster.kube_config.0.cluster_ca_certificate
}

output "host" {
  value = azurerm_kubernetes_cluster.matcha_kubernetes_cluster.kube_config.0.host
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.matcha_kubernetes_cluster.name
}

output "aks_principal_id" {
  value = azurerm_kubernetes_cluster.matcha_kubernetes_cluster.identity[0].principal_id
}
