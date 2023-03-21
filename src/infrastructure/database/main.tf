# create mysql database inside mysql server
resource "azurerm_mysql_flexible_database" "db" {
  name                = var.mysql_database_name
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.server.name
  charset             = "utf8"
  collation           = "utf8_unicode_ci"
  depends_on = [
    azurerm_mysql_flexible_server.server
  ]
}

# download SSL certificate
resource "null_resource" "download-SSL-certificate" {
  provisioner "local-exec" {
    command = "wget https://dl.cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem"
  }
}


# allow all IPs to access the server (required to make server Public for zenml pipelines to access)
resource "azurerm_mysql_flexible_server_firewall_rule" "allow_IPs" {
  name                = "all_traffic"
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.server.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "255.255.255.255"
  depends_on = [
    azurerm_mysql_flexible_server.server
  ]
}
