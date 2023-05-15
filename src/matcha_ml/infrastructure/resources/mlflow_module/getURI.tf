# get URI for  MLflow tracking server
data "kubernetes_service" "mlflow_tracking" {
  metadata {
    name = helm_release.mlflow_tracking.name
  }
}
