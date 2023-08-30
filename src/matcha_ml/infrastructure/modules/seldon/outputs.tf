output "model_deployer_seldon_workloads_namespace" {
  description = "The Kubernetes namespace for Seldon workloads"
  value       = module.seldon.workloads_namespace
}

output "model_deployer_seldon_base_url" {
  description = "The base URL for the Seldon API server"
  value       = module.seldon.base_url
}
