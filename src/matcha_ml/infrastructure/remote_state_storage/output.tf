output "remote_state_storage_account_name" {
  description = "The Azure storage account name for the remote state storage"
  value       = module.state_storage.storage_account_name
}

output "remote_state_storage_container_name" {
  description = "The Azure Blob Storage Container path for remote matcha state"
  value       = module.state_storage.blobstorage_container_path
}

output "remote_state_storage_resource_group_name" {
  description = "Name of the Azure resource group"
  value = module.resource_group.name
}

output "cloud_azure_prefix"{
  description = "The Azure resource group name prefix"
  value = var.prefix
}

output "cloud_azure_location"{
  description = "The Azure location in which the resources are provisioned" 
  value = var.location
}

output "cloud_azure_resource_group_name" {
  description = "Name of the Azure resource group"
  value = module.resource_group.name
}
