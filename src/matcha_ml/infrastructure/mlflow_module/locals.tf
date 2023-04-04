locals {
  kubectl_context = "terraform-${var.aks_cluster_name}-${replace(substr(timestamp(), 0, 16), ":", "_")}"
}
