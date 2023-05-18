# Derived from ZenML's stack recipes; source: https://github.com/zenml-io/mlops-stacks/blob/8eb06596bf836d3a3dd2634fbc7f2b5687421811/aws-minimal/seldon/seldon.tf

# creating the namespace for the seldon deployment
resource "kubernetes_namespace" "seldon_ns" {
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
  namespace = kubernetes_namespace.seldon_ns.metadata[0].name

  set {
    name  = "usageMetrics.enabled"
    value = "true"
  }

  set {
    name  = "istio.enabled"
    value = "true"
  }
}

resource "kubernetes_namespace" "seldon_workloads" {
  metadata {
    name = "matcha-seldon-workloads"
  }
}

# get the ingress host URL for the seldon model deployer
data "kubernetes_service" "seldon_ingress" {
  metadata {
    name      = "istio-ingressgateway"
    namespace = "istio-system"
  }

  depends_on = [
    helm_release.seldon,
    helm_release.istio_ingress
  ]
}
