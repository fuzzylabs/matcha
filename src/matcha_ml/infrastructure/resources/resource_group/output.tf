output "name" {
  description = "Name of the resource group"
  value = data.azurerm_resource_group.main.name
}
