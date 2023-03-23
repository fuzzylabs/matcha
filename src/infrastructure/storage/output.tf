output "storage_container_name" {
  value = azurerm_storage_container.storagecontainer.name
}

output "blobstorage-container-path" {
  value       = "az://${azurerm_storage_container.storagecontainer.name}"
  description = "The Azure Blob Storage Container path for storing your artifacts"
}

output "storage_account_name" {
  value = azurerm_storage_account.storageaccount.name
}

output "primary_access_key" {
  value       = azurerm_storage_account.storageaccount.primary_access_key
  sensitive   = true
  description = "Azure Storage Account - Primary access key"
}

output "secondary_access_key" {
  value       = azurerm_storage_account.storageaccount.secondary_access_key
  sensitive   = true
  description = "Azure Storage Account - Secondary access key"
}

output "primary_connection_string" {
  value       = azurerm_storage_account.storageaccount.primary_connection_string
  sensitive   = true
  description = "Azure Storage Account - Primary connection string"
}

output "secondary_connection_string" {
  value       = azurerm_storage_account.storageaccount.secondary_connection_string
  sensitive   = true
  description = "Azure Storage Account - Secondary connection string"
}

output "primary_blob_connection_string" {
  value       = azurerm_storage_account.storageaccount.primary_blob_connection_string
  sensitive   = true
  description = "Azure Storage Account - Primary Blob service connection string"
}

output "secondary_blob_connection_string" {
  value       = azurerm_storage_account.storageaccount.secondary_blob_connection_string
  sensitive   = true
  description = "Azure Storage Account - Secondary Blob service connection string"
}
