resource "helm_release" "chroma" {
  name       = "chroma"
  chart      = "${path.module}/chroma_helm"
  namespace  = "default"

  values = [file("${path.module}/chroma_helm/values.yaml")]
}
