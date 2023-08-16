output "zenml_storage_container_name" {
  description = "The name of the Azure Storage container used to store ZenML artifacts."
  value = azurerm_storage_container.zenmlstoragecontainer.name
}

output "zenml_blobstorage_container_path" {
  description = "The Azure Blob Storage Container path for storing zenml artifacts"
  value       = "az://${azurerm_storage_container.zenmlstoragecontainer.name}"
}

output "zenml_storage_account_name" {
  description = "The name of the Azure Storage Account used to store ZenML artifacts."
  value = azurerm_storage_account.zenmlaccount.name
}

output "zenml_primary_access_key" {
  description = "ZenML Azure Storage Account - Primary access key"
  value       = azurerm_storage_account.zenmlaccount.primary_access_key
  sensitive   = true
}

output "zenml_secondary_access_key" {
  description = "ZenML Azure Storage Account - Secondary access key"
  value       = azurerm_storage_account.zenmlaccount.secondary_access_key
  sensitive   = true
}

output "zenml_primary_connection_string" {
  description = "ZenML Azure Storage Account - Primary connection string"
  value       = azurerm_storage_account.zenmlaccount.primary_connection_string
  sensitive   = true
}

output "zenml_secondary_connection_string" {
  description = "ZenML Azure Storage Account - Secondary connection string"
  value       = azurerm_storage_account.zenmlaccount.secondary_connection_string
  sensitive   = true
}

output "zenml_primary_blob_connection_string" {
  description = "ZenML Azure Storage Account - Primary Blob service connection string"
  value       = azurerm_storage_account.zenmlaccount.primary_blob_connection_string
  sensitive   = true
}

output "zenml_secondary_blob_connection_string" {
  description = "ZenML Azure Storage Account - Secondary Blob service connection string"
  value       = azurerm_storage_account.zenmlaccount.secondary_blob_connection_string
  sensitive   = true
}
