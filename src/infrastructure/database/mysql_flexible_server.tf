# create azure mysql server
resource "azurerm_mysql_flexible_server" "server" {
  name                   = var.mysql_server_name
  resource_group_name    = var.resource_group_name
  location               = var.location
  administrator_login    = var.mysql_username
  administrator_password = var.mysql_password
  backup_retention_days  = 7
  sku_name               = "B_Standard_B1s"
}

# required for mlflow to work
resource "azurerm_mysql_flexible_server_configuration" "disable_tls" {
  name                = "require_secure_transport"
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.server.name
  value               = "off"
}
