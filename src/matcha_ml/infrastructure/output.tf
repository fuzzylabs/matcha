output "mlflow-tracking-url" {
  value = module.mlflow.mlflow-tracking-url
}

output "seldon-workloads-namespace" {
  value = module.seldon.workloads-namespace
}

output "kubernetes-context" {
  value = local.kubectl_context
}

output "seldon-base-url" {
  value = module.seldon.base-url
}
