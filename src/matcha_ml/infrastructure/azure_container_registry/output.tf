# output for container registry
output "container_registry_url" {
  description = "The URL used to log into the container registry"
  value = azurerm_container_registry.main.login_server
}

output "container_registry_name" {
  description = "The name of the container registry"
  value = azurerm_container_registry.main.name
}
