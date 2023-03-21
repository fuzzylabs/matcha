output "mysql_server_username" {
  value = azurerm_mysql_flexible_server.server.administrator_login

}

output "mysql_server_password" {
  value     = azurerm_mysql_flexible_server.server.administrator_password
  sensitive = true
}

output "mysql_db_host" {
  value = "${azurerm_mysql_flexible_server.server.name}.mysql.database.azure.com"
}

output "mysql_server_name" {
  value = azurerm_mysql_flexible_server.server.name
}

output "mysql_database_name" {
  value = azurerm_mysql_flexible_database.db.name
}

output "mysql_server_port" {
  value = 3306
}
