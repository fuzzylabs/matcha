output "remote_state_storage_path" {
  description = "The Azure Blob Storage Container path for remote matcha state"
  value       = module.state_storage.blobstorage_container_path
}

output "remote_state_storage_account_name" {
  description = "The Azure storage account name for the remote state storage"
  value = module.state_storage.storage_account_name
}
