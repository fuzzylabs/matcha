output "ingress-gateway-spec" {
  value = kubectl_manifest.gateway.live_manifest_incluster
}

output "workloads-namespace" {
  value = kubernetes_namespace.seldon-workloads.metadata[0].name
}

output "base-url" {
  value = data.kubernetes_service.seldon_ingress.status.0.load_balancer.0.ingress.0.ip
}
