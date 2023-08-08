output "mlflow_tracking_url" {
  description = "The tracking URL for MLFlow dashboard"
  value = "http://${data.kubernetes_service.mlflow_tracking.status.0.load_balancer.0.ingress.0.ip}:${data.kubernetes_service.mlflow_tracking.spec.0.port.0.port}"
}
