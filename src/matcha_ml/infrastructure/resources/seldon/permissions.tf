# Allow the default service account in the zenml namespace to access machinelearning.seldon.io

resource "kubernetes_cluster_role_v1" "seldon_machinelearning_permission" {
  metadata {
    name = "seldon-machinelearning-permission"
    labels = {
      app = "zenml"
    }
  }

  rule {
    api_groups = ["*"]
    resources  = ["*"]
    verbs      = ["*"]
  }

  depends_on = [
    helm_release.seldon,
  ]
}

# Bind the cluster role to the default service account in the zenml namespace

resource "kubernetes_cluster_role_binding_v1" "seldon_machinelearning_permission_binding" {
  metadata {
    name = "seldon-machinelearning-permission-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role_v1.seldon_machinelearning_permission.metadata[0].name
  }

  subject {
    kind = "User"
    name = "system:serviceaccount:zenml:default"
  }
}
