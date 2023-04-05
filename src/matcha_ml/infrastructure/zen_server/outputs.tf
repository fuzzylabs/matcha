output "zenserver_url" {
  value = "http://${data.kubernetes_service.zen-server.status.0.load_balancer.0.ingress.0.ip}"
}

output "zenserver_username" {
  value = var.username
}

output "zenserver_password" {
  value     = var.password
  sensitive = true
}

# output "zenserver_url" {
#   value = var.create_ingress_controller ? "https://${data.kubernetes_service.ingress-controller[0].status.0.load_balancer.0.ingress.0.ip}.nip.io/${var.ingress_path}" : "https://${var.ingress_controller_hostname}.nip.io/${var.ingress_path}"
# }

