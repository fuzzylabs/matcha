resource "azurerm_resource_group" "main" {
  name     = "remote-state-storage-resources"
  location = var.location
}
