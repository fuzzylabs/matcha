output "experiment_tracker_mlflow_tracking_url" {
  description = "The URL for the MLflow tracking server"
  value       = module.mlflow.mlflow_tracking_url
}

output "experiment_tracker_mlflow_azure_connection_string" {
  description = "The Azure connection string for the MLflow artifact storage"
  value       = module.storage.primary_connection_string
  sensitive   = true
}
