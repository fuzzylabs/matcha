# get the ingress host URL for the seldon model deployer
data "kubernetes_service" "seldon_ingress" {
  metadata {
    name      = "istio-ingressgateway"
    namespace = "istio-system"
  }
}
