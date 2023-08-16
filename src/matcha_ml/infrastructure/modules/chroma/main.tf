module "chroma" {
  source = "./chroma"

  depends_on = [null_resource.configure_local_kubectl]
}
