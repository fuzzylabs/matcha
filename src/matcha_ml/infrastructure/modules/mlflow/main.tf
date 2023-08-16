module "mlflow" {
  source = "./mlflow_module"

  depends_on = [null_resource.configure_local_kubectl]

  # storage variables
  storage_account_name      = module.storage.storage_account_name
  storage_container_name    = module.storage.storage_container_name
  artifact_azure_access_key = module.storage.primary_access_key
}
