# locals {
#   pvc_manifest = yamldecode(file("${path.module}/chroma-server-index-persistentvolumeclaim.yaml"))
#   deployment_manifest = yamldecode(file("${path.module}/server-deployment.yaml"))
#   service_manifest = yamldecode(file("${path.module}/server-service.yaml"))
# }

# resource "kubernetes_persistent_volume_claim" "pvc" {
#   metadata {
#     name = local.pvc_manifest.metadata.name
#   }

#   spec {
#     access_modes = local.pvc_manifest.spec.accessModes
#     resources {
#       requests = {
#         storage = local.pvc_manifest.spec.resources.requests.storage
#       }
#     }
#     storage_class_name = local.pvc_manifest.spec.storageClassName
#   }
# }

# resource "kubernetes_deployment" "chroma-server" {
#   metadata {
#     name = local.deployment_manifest.metadata.name
#   }

#   spec {
#     selector {
#       match_labels = local.deployment_manifest.spec.selector.matchLabels
#     }

#     template {
#       metadata {
#         labels = local.deployment_manifest.spec.template.metadata.labels
#       }

#       spec {
#         container {
#           name  = local.deployment_manifest.spec.template.spec.containers[0].name
#           image = "chroma-image:latest"  # Set the updated container image here
#           port {
#             container_port = local.deployment_manifest.spec.template.spec.containers[0].ports[0].containerPort
#           }
#         }
#       }
#     }
#   }
# }


locals {
  pvc_manifest = yamldecode(file("${path.module}/chroma-server-index-persistentvolumeclaim.yaml"))
  deployment_manifest = yamldecode(file("${path.module}/server-deployment.yaml"))
  service_manifest = yamldecode(file("${path.module}/server-service.yaml"))
}

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
    labels = {
      "io.kompose.service" = "chroma-server-index"
    }
  }

  spec {
    access_modes = ["ReadWriteOnce"]
    storage_class_name = "standard"
    resources {
      requests = {
        storage = "100Mi"
      }
    }
  }
}


resource "kubernetes_service" "chroma-service" {
  metadata {
    name = local.service_manifest.metadata.name
  }

  spec {
    selector = local.service_manifest.spec.selector

    port {
      name       = local.service_manifest.spec.ports[0].name
      port       = local.service_manifest.spec.ports[0].port
      target_port = local.service_manifest.spec.ports[0].targetPort
    }

    port {
      name       = local.service_manifest.spec.ports[1].name
      port       = local.service_manifest.spec.ports[1].port
      target_port = local.service_manifest.spec.ports[1].targetPort
    }

    port {
      name       = local.service_manifest.spec.ports[2].name
      port       = local.service_manifest.spec.ports[2].port
      target_port = local.service_manifest.spec.ports[2].targetPort
    }

  }
}
