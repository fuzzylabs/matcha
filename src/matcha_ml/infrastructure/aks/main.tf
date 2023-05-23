resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.prefix}-k8s"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.prefix}-k8s"

  default_node_pool {
    name    = "default"
    vm_size = "Standard_DS3_v2"

    enable_auto_scaling = true
    max_count           = 3
    min_count           = 1
  }

  identity {
    type = "SystemAssigned"
  }
}
