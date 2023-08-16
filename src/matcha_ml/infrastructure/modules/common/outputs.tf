output "orchestrator_aks_k8s_context" {
  description = "The name of the Kubernetes context used for deployment"
  value       = local.kubectl_context
}

output "container_registry_azure_registry_url" {
  description = "The URL for the Azure Container Registry"
  value       = module.acr.container_registry_url
}

output "container_registry_azure_registry_name" {
  description = "The name of the Azure Container Registry"
  value       = module.acr.container_registry_name
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
