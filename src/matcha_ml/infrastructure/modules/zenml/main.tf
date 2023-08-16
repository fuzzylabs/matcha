module "zenml_storage" {
  source = "./zenml_storage"

  prefix              = var.prefix
  resource_group_name = module.resource_group.name
  location            = var.location
  aks_principal_id    = module.aks.aks_principal_id
}

module "zenserver" {
  source = "./zen_server"

  depends_on = [null_resource.configure_local_kubectl]

  # resource group variables
  resource_group_name = module.resource_group.name
  location            = var.location
  prefix              = var.prefix

  # ZenServer credentials
  username = var.username
  password = var.password

  zenmlserver_version = var.zenmlserver_version
}
