resource "azurerm_user_assigned_identity" "managed_identity" {
  name                = "${var.prefix}-managed-identity"
  location            = var.location
  resource_group_name = var.resource_group_name
}
