# creating the namespace for the seldon deployment
resource "kubernetes_namespace" "seldon-ns" {
  metadata {
    name = var.seldon_namespace
  }
}

# creating the seldon deployment
resource "helm_release" "seldon" {

  name       = var.seldon_name
  repository = "https://storage.googleapis.com/seldon-charts"
  chart      = "seldon-core-operator"
  # dependency on seldon-ns
  namespace = kubernetes_namespace.seldon-ns.metadata[0].name

  set {
    name  = "usageMetrics.enabled"
    value = "true"
  }

  set {
    name  = "istio.enabled"
    value = "true"
  }
}
