data "kubernetes_service" "zen-server" {
  metadata {
    name      = helm_release.zen-server.name
    namespace = helm_release.zen-server.namespace
  }

}
