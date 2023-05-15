# set up local kubectl client to access the newly created cluster
resource "null_resource" "configure_local_kubectl" {
  provisioner "local-exec" {
    command = "az aks get-credentials --resource-group ${module.resource_group.name} --name ${module.aks.aks_cluster_name} --context ${local.kubectl_context} --overwrite-existing"
  }
}

locals {
  kubectl_context = "terraform-${module.aks.aks_cluster_name}-${replace(substr(timestamp(), 0, 16), ":", "_")}"
}
