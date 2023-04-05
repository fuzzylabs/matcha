data "kubernetes_service" "zen_server" {
  metadata {
    name      = "${var.prefix}-zenserver"
    namespace = "${var.prefix}-${var.namespace}"
  }

  depends_on = [
    helm_release.zen-server
  ]
}
