output "mlflow-tracking-url" {
  value = module.mlflow.mlflow-tracking-url
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
  value = module.acr.container-registry-URL
}
