output "kube_config" {
  description = "Raw Kubernetes configuration for the created cluster"
  value     = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive = true
}

output "client_key" {
  description = "Client key for accessing the Kubernetes cluster"
  value = azurerm_kubernetes_cluster.main.kube_config.0.client_key
}

output "client_certificate" {
  description = "Client certificate for accessing the Kubernetes cluster"
  value     = azurerm_kubernetes_cluster.main.kube_config.0.client_certificate
  sensitive = true
}

output "cluster_ca_certificate" {
  description = "Cluster CA certificate for the Kubernetes cluster"
  value = azurerm_kubernetes_cluster.main.kube_config.0.cluster_ca_certificate
}

output "host" {
  description = "Host address for the Kubernetes cluster"
  value = azurerm_kubernetes_cluster.main.kube_config.0.host
}

output "aks_cluster_id" {
  description = "ID of the created Kubernetes cluster"
  value = azurerm_kubernetes_cluster.main.id
}

output "aks_cluster_name" {
  description = "Name of the created Kubernetes cluster"
  value = azurerm_kubernetes_cluster.main.name
}

output "aks_principal_id" {
  description = "Principal ID for the Kubernetes cluster"
  value = azurerm_kubernetes_cluster.main.identity[0].principal_id
}

output "aks_object_id" {
  description = "Object ID for the Kubernetes cluster"
  value = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}
