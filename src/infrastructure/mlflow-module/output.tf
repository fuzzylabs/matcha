output "ingress-controller-name" {
  value = helm_release.nginx-controller.name
}

output "ingress-controller-namespace" {
  value = kubernetes_namespace.nginx-ns.metadata[0].name
}

output "mlflow-namespace" {
  value = kubernetes_namespace.mlflow.metadata[0].name
}

output "mlflow-tracking-URL" {
  value = data.kubernetes_service.mlflow_tracking.status.0.load_balancer.0.ingress.0.ip
}

output "mlflow-username" {
  value = var.mlflow_username
}

output "mlflow-password" {
  value     = var.mlflow_password
  sensitive = true
}
