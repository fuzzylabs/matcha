output "zenml_storage_container_name" {
  value = azurerm_storage_container.zenmlstoragecontainer.name
}

output "zenml_blobstorage_container_path" {
  value       = "az://${azurerm_storage_container.zenmlstoragecontainer.name}"
  description = "The Azure Blob Storage Container path for storing zenml artifacts"
}

output "zenml_storage_account_name" {
  value = azurerm_storage_account.zenmlaccount.name
}

output "zenml_primary_access_key" {
  value       = azurerm_storage_account.zenmlaccount.primary_access_key
  sensitive   = true
  description = "ZenML Azure Storage Account - Primary access key"
}

output "zenml_secondary_access_key" {
  value       = azurerm_storage_account.zenmlaccount.secondary_access_key
  sensitive   = true
  description = "ZenML Azure Storage Account - Secondary access key"
}

output "zenml_primary_connection_string" {
  value       = azurerm_storage_account.zenmlaccount.primary_connection_string
  sensitive   = true
  description = "ZenML Azure Storage Account - Primary connection string"
}

output "zenml_secondary_connection_string" {
  value       = azurerm_storage_account.zenmlaccount.secondary_connection_string
  sensitive   = true
  description = "ZenML Azure Storage Account - Secondary connection string"
}

output "zenml_primary_blob_connection_string" {
  value       = azurerm_storage_account.zenmlaccount.primary_blob_connection_string
  sensitive   = true
  description = "ZenML Azure Storage Account - Primary Blob service connection string"
}

output "zenml_secondary_blob_connection_string" {
  value       = azurerm_storage_account.zenmlaccount.secondary_blob_connection_string
  sensitive   = true
  description = "ZenML Azure Storage Account - Secondary Blob service connection string"
}
