resource "kubernetes_namespace" "k8s-ns" {
  metadata {
    name = "zenml"
  }
}
