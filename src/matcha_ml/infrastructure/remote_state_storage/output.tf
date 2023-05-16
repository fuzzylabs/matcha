output "remote_state_storage_path" {
  description = "The Azure Blob Storage Container path for remote matcha state"
  value       = module.state_storage.blobstorage_container_path
}
