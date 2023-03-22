# create the mlflow tracking server namespace
resource "kubernetes_namespace" "mlflow" {
  metadata {
    name = var.mlflow_namespace
  }
}

# create the mlflow tracking server deployment using mlflow helm charts
# Reference: https://github.com/community-charts/helm-charts/blob/main/charts/mlflow/values.yaml
resource "helm_release" "mlflow-tracking" {

  name       = "mlflow-tracking"
  repository = "https://community-charts.github.io/helm-charts"
  chart      = "mlflow"
  namespace  = kubernetes_namespace.mlflow.metadata[0].name

  # set proxied access to artifact storage
  set {
    name  = "artifactRoot.proxiedArtifactStorage"
    value = var.artifact_Proxied_Access
    type  = "auto"
  }

  # set values for Azure Blob Storage
  set {
    name  = "artifactRoot.azureBlob.enabled"
    value = var.artifact_Azure
    type  = "auto"
  }
  set {
    name  = "artifactRoot.azureBlob.storageAccount"
    value = var.storage_account_name
    type  = "string"
  }
  set {
    name  = "artifactRoot.azureBlob.container"
    value = var.storage_container_name
    type  = "string"
  }
  set_sensitive {
    name  = "artifactRoot.azureBlob.accessKey"
    value = var.artifact_Azure_Access_Key
    type  = "string"
  }

  depends_on = [
    resource.kubernetes_namespace.mlflow
  ]
}
