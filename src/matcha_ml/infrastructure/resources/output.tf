output "experiment_tracker_mlflow_tracking_url" {
  description = "The URL for the MLflow tracking server"
  value       = module.mlflow.mlflow_tracking_url
}

output "experiment_tracker_mlflow_azure_connection_string" {
  description = "The Azure connection string for the MLflow artifact storage"
  value       = module.storage.primary_connection_string
  sensitive   = true
}

output "pipeline_zenml_storage_path" {
  description = "The Azure Blob Storage Container path for storing ZenML artifacts"
  value       = module.zenml_storage.zenml_blobstorage_container_path
}


output "pipeline_zenml_connection_string" {
  description = "The primary connection string for the ZenML Azure Storage Account"
  value       = module.zenml_storage.zenml_primary_connection_string
  sensitive   = true
}

output "orchestrator_aks_k8s_context" {
  description = "The name of the Kubernetes context used for deployment"
  value       = local.kubectl_context
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

output "container_registry_azure_registry_url" {
  description = "The URL for the Azure Container Registry"
  value       = module.acr.container_registry_url
}

output "container_registry_azure_registry_name" {
  description = "The name of the Azure Container Registry"
  value       = module.acr.container_registry_name
}

output "model_deployer_seldon_workloads_namespace" {
  description = "The Kubernetes namespace for Seldon workloads"
  value       = module.seldon.workloads_namespace
}

output "model_deployer_seldon_base_url" {
  description = "The base URL for the Seldon API server"
  value       = module.seldon.base_url
}

output "cloud_azure_resource_group_name" {
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