output "data_version_control_primary_connection_string"{
  description = "The primary connection string for the ZenML Azure Storage Account"
  value = module.data_version_control_storage.primary_connection_string
  sensitive = true
}

output "data_version_control_storage_container_name"{
  description = "The name of the container used for data version control"
  value = module.data_version_control_storage.storage_container_name
}

output "data_version_control_storage_account_name"{
  description = "The name of the storage account for data version control"
  value = module.data_version_control_storage.storage_account_name
}
