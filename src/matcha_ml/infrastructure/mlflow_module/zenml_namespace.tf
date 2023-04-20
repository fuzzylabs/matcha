resource "kubernetes_namespace" "k8s_ns" {
  metadata {
    name = "zenml"
  }
}
