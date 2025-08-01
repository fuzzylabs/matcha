# Reference: https://github.com/hashicorp/terraform-provider-azurerm/tree/main/examples/storage/storage-container

# create a storage account
resource "azurerm_storage_account" "storageaccount" {
  name                = "st${var.prefix}acc"
  resource_group_name = var.resource_group_name
  location            = var.location

  account_tier                    = "Standard"
  account_kind                    = "StorageV2"
  account_replication_type        = "LRS"
  access_tier                     = "Hot"
  allow_nested_items_to_be_public = true
}

# create a storage container inside created storage account
resource "azurerm_storage_container" "storagecontainer" {
  name                  = "${var.prefix}store"
  storage_account_id    = azurerm_storage_account.storageaccount.id
  container_access_type = "container"
}
