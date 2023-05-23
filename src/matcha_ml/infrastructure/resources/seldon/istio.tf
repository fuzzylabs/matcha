# Derived from ZenML's stack recipes; source: https://github.com/zenml-io/mlops-stacks/blob/8eb06596bf836d3a3dd2634fbc7f2b5687421811/aws-minimal/seldon/istio.tf

# create a namespace for istio resources
resource "kubernetes_namespace" "istio_ns" {
  metadata {
    name = "istio-system"
    labels = {
      istio-injection = "enabled"
    }
  }
}

# istio-base creates the istio definitions that will be used going forward
resource "helm_release" "istio_base" {
  name       = "istio-base-seldon"
  repository = "https://istio-release.storage.googleapis.com/charts"
  chart      = "base"

  # adding a dependency on the istio-namespace
  namespace = kubernetes_namespace.istio_ns.metadata[0].name
}

# the istio daemon
resource "helm_release" "istiod" {
  name       = "istiod-seldon"
  repository = helm_release.istio_base.repository # dependency on istio-base 
  chart      = "istiod"

  namespace = kubernetes_namespace.istio_ns.metadata[0].name
}

# the istio ingress gateway
# cannot use kubernetes_manifest resource since it practically 
# doesn't support CRDs. Going with kubectl instead.
resource "kubectl_manifest" "gateway" {
  yaml_body = <<YAML
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: seldon-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway # use istio default controller
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
YAML    
  # depencdency on istio-d
  override_namespace = helm_release.istiod.namespace
}

# creating the ingress gateway definitions
resource "helm_release" "istio_ingress" {
  name       = "istio-ingressgateway"
  repository = helm_release.istiod.repository
  chart      = "gateway"

  # dependency on istio-ingress-ns
  namespace = kubernetes_namespace.istio_ns.metadata[0].name
}
