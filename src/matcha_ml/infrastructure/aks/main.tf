resource "azurerm_kubernetes_cluster" "matcha_kubernetes_cluster" {
  name                = "${var.prefix}-k8s"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.prefix}-k8s"

  default_node_pool {
    name    = "default"
    vm_size = "Standard_DS2_v2"

    enable_auto_scaling = true
    max_count           = 3
    min_count           = 1
    node_count          = 2
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "kubernetes_namespace" "k8s-ns" {
  metadata {
    name = "zenml"
  }
}
