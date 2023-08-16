module "data_version_control_storage" {
  source = "./data_version_control_storage"

  resource_group_name = module.resource_group.name
  prefix              = var.prefix
  location            = var.location
}
