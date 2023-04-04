resource "azurerm_container_registry" "container_registry" {
  name                = "cr${var.prefix}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Standard"
}

resource "azurerm_role_assignment" "aks_acr_access" {
  principal_id                     = var.aks_object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.container_registry.id
  skip_service_principal_aad_check = true
}
