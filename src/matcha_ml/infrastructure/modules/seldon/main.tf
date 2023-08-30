
module "seldon" {
  source = "./seldon"

  depends_on = [null_resource.configure_local_kubectl]

  # details about the seldon deployment
  seldon_name      = var.seldon_name
  seldon_namespace = var.seldon_namespace

}
