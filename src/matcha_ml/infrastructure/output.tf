output "mlflow-tracking-url" {
  value = module.mlflow.mlflow_tracking_url
}

output "zenml-storage-path" {
  value = module.zenml_storage.zenml_blobstorage_container_path
}

output "zenml-connection-string" {
  value     = module.zenml_storage.zenml_primary_connection_string
  sensitive = true
}

output "k8s-context" {
  value = local.kubectl_context
}

output "zen-server-url" {
  value = module.zenserver.zenserver_url
}

output "zen-server-username" {
  value = module.zenserver.zenserver_username
}

output "zen-server-password" {
  value     = module.zenserver.zenserver_password
  sensitive = true
}

output "azure-container-registry" {
  value = module.acr.container_registry_url
}

output "azure-registry-name" {
  value = module.acr.container_registry_name
}

output "seldon-workloads-namespace" {
  value = module.seldon.workloads_namespace
}

output "seldon-base-url" {
  value = module.seldon.base_url
}

output "resource-group-name" {
  value = module.resource_group.name
}
