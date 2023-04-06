# output for container registry
output "container_registry_url" {
  value = azurerm_container_registry.container_registry.login_server
}

output "container_registry_name" {
  value = azurerm_container_registry.container_registry.name
}
