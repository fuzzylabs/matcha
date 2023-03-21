# get URI for  MLflow tracking server
data "kubernetes_service" "mlflow_tracking" {
  metadata {
    name      = "${helm_release.nginx-controller.name}-ingress-nginx-controller"
    namespace = kubernetes_namespace.nginx-ns.metadata[0].name
  }
}
