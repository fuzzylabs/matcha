# set up local kubectl client to access the newly created cluster
resource "null_resource" "configure-local-kubectl" {
  provisioner "local-exec" {
    command = "az aks get-credentials --resource-group ${var.resource_group_name} --name ${var.aks_cluster_name} --context ${local.kubectl_context} --overwrite-existing"
  }
}
