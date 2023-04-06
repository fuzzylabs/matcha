data "kubernetes_service" "zen_server" {
  metadata {
    name      = "${helm_release.zen-server.name}-zenml"
    namespace = helm_release.zen-server.namespace
  }

  depends_on = [
    helm_release.zen-server
  ]
}
