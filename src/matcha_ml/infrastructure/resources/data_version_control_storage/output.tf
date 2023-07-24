output "storage_container_name" {
  description = "The name of the Azure Storage Container."
  value = azurerm_storage_container.storagecontainer.name
}

output "storage_account_name" {
  description = "The name of the Azure Storage Account."
  value       = azurerm_storage_account.storageaccount.name
}

output "primary_connection_string" {
  description = "Azure Storage Account - Primary connection string"
  value       = azurerm_storage_account.storageaccount.primary_connection_string
  sensitive   = true
}