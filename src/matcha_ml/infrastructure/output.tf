output "mlflow-tracking-url" {
  value = module.mlflow.mlflow-tracking-url
}

output "zenml-storage-path" {
  value = module.zenml_storage.zenml_blobstorage_container_path
}

output "zenml-connection-string" {
  value     = module.zenml_storage.primary_connection_string
  sensitive = true
}

output "k8s-context" {
  value = module.mlflow.k8s-context
}
