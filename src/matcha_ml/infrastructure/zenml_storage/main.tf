# Reference: https://github.com/hashicorp/terraform-provider-azurerm/tree/main/examples/storage/storage-container

# create a storage account
resource "azurerm_storage_account" "zenmlaccount" {
  name                = "${var.prefix}zenmlacc"
  resource_group_name = var.resource_group_name
  location            = var.location

  account_tier             = "Standard"
  account_kind             = "StorageV2"
  account_replication_type = "LRS"
}

# create a storage container inside created storage account
resource "azurerm_storage_container" "zenmlstoragecontainer" {
  name                  = "${var.prefix}artifactstore"
  storage_account_name  = azurerm_storage_account.zenmlaccount.name
  container_access_type = "private"
}


data "azurerm_storage_account" "zenmlaccount" {
  name                = azurerm_storage_account.zenmlaccount.name
  resource_group_name = var.resource_group_name
}

resource "azurerm_role_assignment" "zenmlstorage" {
  scope                = azurerm_storage_account.zenmlaccount.id
  role_definition_name = "Contributor"
  principal_id         = var.aks_principal_id
}
