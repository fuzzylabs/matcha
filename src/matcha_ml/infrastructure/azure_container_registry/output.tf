# output for container registry
output "container-registry-URL" {
  value = azurerm_container_registry.container_registry.login_server
}
