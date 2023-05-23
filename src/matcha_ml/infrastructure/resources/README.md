## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.14.8 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | >=3.16.0 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | ~> 2.0.1 |
| <a name="requirement_htpasswd"></a> [htpasswd](#requirement\_htpasswd) | 1.0.4 |
| <a name="requirement_kubectl"></a> [kubectl](#requirement\_kubectl) | 1.14.0 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | ~> 2.11.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | 2.1.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | 3.2.1 |
| <a name="requirement_random"></a> [random](#requirement\_random) | 3.1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_external"></a> [external](#provider\_external) | 2.3.1 |
| <a name="provider_null"></a> [null](#provider\_null) | 3.2.1 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_acr"></a> [acr](#module\_acr) | ./azure_container_registry | n/a |
| <a name="module_aks"></a> [aks](#module\_aks) | ./aks | n/a |
| <a name="module_mlflow"></a> [mlflow](#module\_mlflow) | ./mlflow_module | n/a |
| <a name="module_resource_group"></a> [resource\_group](#module\_resource\_group) | ./resource_group | n/a |
| <a name="module_seldon"></a> [seldon](#module\_seldon) | ./seldon | n/a |
| <a name="module_storage"></a> [storage](#module\_storage) | ./storage | n/a |
| <a name="module_zenml_storage"></a> [zenml\_storage](#module\_zenml\_storage) | ./zenml_storage | n/a |
| <a name="module_zenserver"></a> [zenserver](#module\_zenserver) | ./zen_server | n/a |

## Resources

| Name | Type |
|------|------|
| [null_resource.configure_local_kubectl](https://registry.terraform.io/providers/hashicorp/null/3.2.1/docs/resources/resource) | resource |
| [external_external.os](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_location"></a> [location](#input\_location) | The Azure Region in which all resources should be provisioned | `string` | n/a | yes |
| <a name="input_password"></a> [password](#input\_password) | Password for ZenServer | `string` | n/a | yes |
| <a name="input_prefix"></a> [prefix](#input\_prefix) | A prefix used for all resources | `string` | `"matcha"` | no |
| <a name="input_seldon_name"></a> [seldon\_name](#input\_seldon\_name) | Name of the Seldon deployment | `string` | `"seldon"` | no |
| <a name="input_seldon_namespace"></a> [seldon\_namespace](#input\_seldon\_namespace) | Namespace for Seldon resources | `string` | `"seldon-system"` | no |
| <a name="input_username"></a> [username](#input\_username) | Username for ZenServer | `string` | `"default"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_azure_container_registry"></a> [azure\_container\_registry](#output\_azure\_container\_registry) | The URL for the Azure Container Registry |
| <a name="output_azure_registry_name"></a> [azure\_registry\_name](#output\_azure\_registry\_name) | The name of the Azure Container Registry |
| <a name="output_k8s_context"></a> [k8s\_context](#output\_k8s\_context) | The name of the Kubernetes context used for deployment |
| <a name="output_mlflow_tracking_url"></a> [mlflow\_tracking\_url](#output\_mlflow\_tracking\_url) | The URL for the MLflow tracking server |
| <a name="output_seldon_base_url"></a> [seldon\_base\_url](#output\_seldon\_base\_url) | The base URL for the Seldon API server |
| <a name="output_seldon_workloads_namespace"></a> [seldon\_workloads\_namespace](#output\_seldon\_workloads\_namespace) | The Kubernetes namespace for Seldon workloads |
| <a name="output_zen_server_password"></a> [zen\_server\_password](#output\_zen\_server\_password) | The password for accessing the ZenServer API server |
| <a name="output_zen_server_url"></a> [zen\_server\_url](#output\_zen\_server\_url) | The URL for the ZenServer API server |
| <a name="output_zen_server_username"></a> [zen\_server\_username](#output\_zen\_server\_username) | The username for accessing the ZenServer API server |
| <a name="output_zenml_connection_string"></a> [zenml\_connection\_string](#output\_zenml\_connection\_string) | The primary connection string for the ZenML Azure Storage Account |
| <a name="output_zenml_storage_path"></a> [zenml\_storage\_path](#output\_zenml\_storage\_path) | The Azure Blob Storage Container path for storing ZenML artifacts |
