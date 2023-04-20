output "mlflow_tracking_url" {
  description = "The URL for the MLflow tracking server"
  value       = module.mlflow.mlflow_tracking_url
}

output "zenml_storage_path" {
  description = "The Azure Blob Storage Container path for storing ZenML artifacts"
  value       = module.zenml_storage.zenml_blobstorage_container_path
}

output "zenml_connection_string" {
  description = "The primary connection string for the ZenML Azure Storage Account"
  value       = module.zenml_storage.zenml_primary_connection_string
  sensitive   = true
}

output "k8s_context" {
  description = "The name of the Kubernetes context used for deployment"
  value       = local.kubectl_context
}

output "zen_server_url" {
  description = "The URL for the ZenServer API server"
  value       = module.zenserver.zenserver_url
}

output "zen_server_username" {
  description = "The username for accessing the ZenServer API server"
  value       = module.zenserver.zenserver_username
}

output "zen_server_password" {
  description = "The password for accessing the ZenServer API server"
  value       = module.zenserver.zenserver_password
  sensitive   = true
}

output "azure_container_registry" {
  description = "The URL for the Azure Container Registry"
  value       = module.acr.container_registry_url
}

output "azure_registry_name" {
  description = "The name of the Azure Container Registry"
  value       = module.acr.container_registry_name
}

output "seldon_workloads_namespace" {
  description = "The Kubernetes namespace for Seldon workloads"
  value       = module.seldon.workloads_namespace
}

output "seldon_base_url" {
  description = "The base URL for the Seldon API server"
  value       = module.seldon.base_url
}

output "resource-group-name" {
  value = module.resource_group.name
}
