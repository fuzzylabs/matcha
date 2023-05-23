# Derived from ZenML's stack recipes; source: https://github.com/zenml-io/mlops-stacks/blob/8eb06596bf836d3a3dd2634fbc7f2b5687421811/aws-minimal/configure_kubectl.tf

# set up local kubectl client to access the newly created cluster
resource "null_resource" "configure_local_kubectl" {
  provisioner "local-exec" {
    command = "az aks get-credentials --resource-group ${module.resource_group.name} --name ${module.aks.aks_cluster_name} --context ${local.kubectl_context} --overwrite-existing"
  }
}

locals {
  kubectl_context = "terraform-${module.aks.aks_cluster_name}-${replace(substr(timestamp(), 0, 16), ":", "_")}"
}
