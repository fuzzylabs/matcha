output "zenserver_url" {
  description = "The URL for the ZenML server"
  value = "http://${data.kubernetes_service.zen_server.status.0.load_balancer.0.ingress.0.ip}"
}

output "zenserver_username" {
  description = "The username used to access the ZenML server"
  value = var.username
}

output "zenserver_password" {
  description = "The password used to access the ZenML server"
  value     = var.password
  sensitive = true
}
