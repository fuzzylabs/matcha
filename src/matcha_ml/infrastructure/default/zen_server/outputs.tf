output "zenserver_username" {
  description = "The username used to access the ZenML server"
  value = var.username
}

output "zenserver_password" {
  description = "The password used to access the ZenML server"
  value     = var.password
  sensitive = true
}
