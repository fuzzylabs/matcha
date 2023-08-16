output "pipeline_zenml_storage_path" {
  description = "The Azure Blob Storage Container path for storing ZenML artifacts"
  value       = module.zenml_storage.zenml_blobstorage_container_path
}


output "pipeline_zenml_connection_string" {
  description = "The primary connection string for the ZenML Azure Storage Account"
  value       = module.zenml_storage.zenml_primary_connection_string
  sensitive   = true
}

output "pipeline_zenml_server_url" {
  description = "The URL for the ZenServer API server"
  value       = module.zenserver.zenserver_url
}

output "pipeline_zenml_server_username" {
  description = "The username for accessing the ZenServer API server"
  value       = module.zenserver.zenserver_username
}

output "pipeline_zenml_server_password" {
  description = "The password for accessing the ZenServer API server"
  value       = module.zenserver.zenserver_password
  sensitive   = true
}
