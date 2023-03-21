# create a secret with user credentials
resource "kubernetes_secret" "name" {
  metadata {
    name      = "basic-auth"
    namespace = kubernetes_namespace.mlflow.metadata[0].name
  }

  type = "Opaque"
  # the key should be auth for nginx ingress to work
  # throws a 503 error if the key is not auth
  data = {
    "auth" = "${var.mlflow-username}:${htpasswd_password.hash.apr1}"
  }
}

# hash the password required for nginx
resource "htpasswd_password" "hash" {
  password = var.mlflow-password
}
