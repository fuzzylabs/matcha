# create the mlflow tracking server deployment using mlflow helm charts
# Reference: https://github.com/community-charts/helm-charts/blob/main/charts/mlflow/values.yaml
resource "helm_release" "mlflow_tracking" {

  name       = "mlflow-tracking"
  repository = "https://community-charts.github.io/helm-charts"
  chart      = "mlflow"
  version    = "1.3.2"

  # Change type from "ClusterIP" to "LoadBalancer"
  set = [
    {
      name  = "service.type"
      value = "LoadBalancer"
    },
    # set proxied access to artifact storage
    {
      name  = "artifactRoot.proxiedArtifactStorage"
      value = var.artifact_proxied_access
      type  = "auto"
    },

    # Derived from ZenML's stack recipes; source: https://github.com/zenml-io/mlops-stacks/blob/8eb06596bf836d3a3dd2634fbc7f2b5687421811/aws-minimal/mlflow-module/mlflow.tf#L39
    # set values for Azure Blob Storage
    {
      name  = "artifactRoot.azureBlob.enabled"
      value = var.artifact_azure
      type  = "auto"
    },
    {
      name  = "artifactRoot.azureBlob.storageAccount"
      value = var.storage_account_name
      type  = "string"
    },
    {
      name  = "artifactRoot.azureBlob.container"
      value = var.storage_container_name
      type  = "string"
    },
    {
      name  = "artifactRoot.azureBlob.accessKey"
      value = var.artifact_azure_access_key
      type  = "string"
    },
  ]
}
