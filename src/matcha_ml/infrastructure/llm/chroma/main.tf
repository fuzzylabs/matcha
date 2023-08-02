resource "kubernetes_deployment" "chroma-server" {
  metadata {
    name = "chroma-server"
  }

  spec {
    selector {
      match_labels = {
        app = "chroma-server"
      }
    }

    template {
      metadata {
        labels = {
          app = "chroma-server"
        }
      }

      spec {
        container {
          name  = "chroma-server"
          image = "ghcr.io/chroma-core/chroma:0.4.3"
          port {
            container_port = 8000
          }
          resources {
            requests = {
              memory = "256Mi"
              cpu    = "256m"
            }
            limits = {
              memory = "2Gi"
              cpu    = "2"
            }
          }
          volume_mount {
            mount_path = "/index_data"
            name       = "chroma-server-index"
          }
        }

        restart_policy = "Always"

        volume {
          name = "chroma-server-index"
          persistent_volume_claim {
            claim_name = "chroma-server-index"
          }
        }
      }
    }
  }
}

resource "kubernetes_persistent_volume_claim" "pvc" {
  metadata {
    name = "chroma-server-index"
  }

  spec {
    access_modes = ["ReadWriteOnce"]
    storage_class_name = "default"
    resources {
      requests = {
        storage = "100Mi"
      }
    }
  }
}

resource "kubernetes_service" "chroma-service" {
  metadata {
    name = "chroma-service"
  }

  spec {
    selector = {"app": "chroma-server"}

    port {
      name       = "8123"
      port       = 8123
      target_port = 8123
    }

    port {
      name       = "9000"
      port       = 9000
      target_port = 9000
    }

    port {
      name       = "8000"
      port       = 8000
      target_port = 8000
    }

  }
}
