resource "azurerm_container_registry" "main" {
  name                = "cr${var.prefix}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Standard"
}

resource "azurerm_role_assignment" "aks_acr_access" {
  scope                            = azurerm_container_registry.main.id
  role_definition_name             = "AcrPull"
  principal_id                     = var.aks_object_id
  skip_service_principal_aad_check = true
}
