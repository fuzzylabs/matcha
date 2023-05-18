output "client_id" {
    description = "The Azure client ID"
  value = azurerm_user_assigned_identity.managed_identity.client_id
} 
