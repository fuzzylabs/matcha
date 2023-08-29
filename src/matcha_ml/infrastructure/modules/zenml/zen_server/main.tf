# Derived from ZenML's stack recipes; source: https://github.com/zenml-io/mlops-stacks/blob/8eb06596bf836d3a3dd2634fbc7f2b5687421811/modules/zenml-module/zen_server.tf

# create the ZenServer deployment
resource "kubernetes_namespace" "zen_server" {
  metadata {
    name = "${var.prefix}-${var.namespace}"
  }
}

resource "helm_release" "zen_server" {

  name      = "${var.prefix}-zenserver"
  chart     = "${path.module}/zenml_helm"
  namespace = kubernetes_namespace.zen_server.metadata[0].name

  set {
    name  = "zenml.image.repository"
    value = var.zenmlserver_image_repo
  }

  set {
    name  = "zenml.defaultUsername"
    value = var.username
  }
  set {
    name  = "zenml.defaultPassword"
    value = var.password
  }
  set {
    name  = "zenml.deploymentType"
    value = "azure"
  }
  set {
    name  = "zenml.analyticsOptIn"
    value = var.analytics_opt_in
  }

  # set parameters for the mysql database
  set {
    name  = "zenml.database.url"
    value = var.deploy_db ? "mysql://${var.database_username}:${azurerm_mysql_flexible_server.mysql[0].administrator_password}@${azurerm_mysql_flexible_server.mysql[0].name}.mysql.database.azure.com:3306/${var.db_name}" : var.database_url
  }
  set {
    name  = "zenml.database.sslCa"
    value = var.deploy_db ? "" : var.database_ssl_ca
  }
  set {
    name  = "zenml.database.sslCert"
    value = var.deploy_db ? "" : var.database_ssl_cert
  }
  set {
    name  = "zenml.database.sslKey"
    value = var.deploy_db ? "" : var.database_ssl_key
  }
  set {
    name  = "zenml.database.sslVerifyServerCert"
    value = var.deploy_db ? false : var.database_ssl_verify_server_cert
  }
  set {
    name = "zenml.image.tag"
    value = var.zenmlserver_version
  }
  depends_on = [
    resource.kubernetes_namespace.zen_server
  ]
}
