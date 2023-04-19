output "storage_container_name" {
  description = "The name of the Azure Storage Container."
  value = azurerm_storage_container.storagecontainer.name
}

output "blobstorage_container_path" {
  description = "The Azure Blob Storage Container path for storing your artifacts"
  value       = "az://${azurerm_storage_container.storagecontainer.name}"
}

output "storage_account_name" {
  description = "The name of the Azure Storage Account."
  value = azurerm_storage_account.storageaccount.name
}

output "primary_access_key" {
  description = "Azure Storage Account - Primary access key"
  value       = azurerm_storage_account.storageaccount.primary_access_key
  sensitive   = true
}

output "secondary_access_key" {
  description = "Azure Storage Account - Secondary access key"
  value       = azurerm_storage_account.storageaccount.secondary_access_key
  sensitive   = true
}

output "primary_connection_string" {
  description = "Azure Storage Account - Primary connection string"
  value       = azurerm_storage_account.storageaccount.primary_connection_string
  sensitive   = true
}

output "secondary_connection_string" {
  description = "Azure Storage Account - Secondary connection string"
  value       = azurerm_storage_account.storageaccount.secondary_connection_string
  sensitive   = true
}

output "primary_blob_connection_string" {
  description = "Azure Storage Account - Primary Blob service connection string"
  value       = azurerm_storage_account.storageaccount.primary_blob_connection_string
  sensitive   = true
}

output "secondary_blob_connection_string" {
  description = "Azure Storage Account - Secondary Blob service connection string"
  value       = azurerm_storage_account.storageaccount.secondary_blob_connection_string
  sensitive   = true
}
