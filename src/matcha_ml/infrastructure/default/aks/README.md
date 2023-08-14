## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_kubernetes_cluster.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_location"></a> [location](#input\_location) | The Azure region where the Kubernetes cluster will be created | `string` | n/a | yes |
| <a name="input_prefix"></a> [prefix](#input\_prefix) | Prefix to be used for all resources in this module | `string` | n/a | yes |
| <a name="input_resource_group_name"></a> [resource\_group\_name](#input\_resource\_group\_name) | The name of the resource group to create the Kubernetes cluster in | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_aks_cluster_id"></a> [aks\_cluster\_id](#output\_aks\_cluster\_id) | ID of the created Kubernetes cluster |
| <a name="output_aks_cluster_name"></a> [aks\_cluster\_name](#output\_aks\_cluster\_name) | Name of the created Kubernetes cluster |
| <a name="output_aks_object_id"></a> [aks\_object\_id](#output\_aks\_object\_id) | Object ID for the Kubernetes cluster |
| <a name="output_aks_principal_id"></a> [aks\_principal\_id](#output\_aks\_principal\_id) | Principal ID for the Kubernetes cluster |
| <a name="output_client_certificate"></a> [client\_certificate](#output\_client\_certificate) | Client certificate for accessing the Kubernetes cluster |
| <a name="output_client_key"></a> [client\_key](#output\_client\_key) | Client key for accessing the Kubernetes cluster |
| <a name="output_cluster_ca_certificate"></a> [cluster\_ca\_certificate](#output\_cluster\_ca\_certificate) | Cluster CA certificate for the Kubernetes cluster |
| <a name="output_host"></a> [host](#output\_host) | Host address for the Kubernetes cluster |
| <a name="output_kube_config"></a> [kube\_config](#output\_kube\_config) | Raw Kubernetes configuration for the created cluster |
