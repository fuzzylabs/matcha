resource "azurerm_resource_group" "matcha_resource_group" {
  name     = "${var.prefix}-resources"
  location = var.location
}
