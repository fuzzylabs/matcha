output "ingress_gateway_spec" {
  description = "The YAML specification for the Istio ingress gateway"
  value = kubectl_manifest.gateway.live_manifest_incluster
}

output "workloads_namespace" {
  description = "The namespace for Seldon workloads"
  value = kubernetes_namespace.seldon_workloads.metadata[0].name
}

output "base_url" {
  description = "The base URL of the Seldon deployment"
  value = data.kubernetes_service.seldon_ingress.status.0.load_balancer.0.ingress.0.ip
}
