## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.14.8 |
| <a name="requirement_htpasswd"></a> [htpasswd](#requirement\_htpasswd) | 1.0.4 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_helm"></a> [helm](#provider\_helm) | n/a |
| <a name="provider_kubernetes"></a> [kubernetes](#provider\_kubernetes) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [helm_release.mlflow-tracking](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/resources/release) | resource |
| [kubernetes_namespace.k8s_ns](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/resources/namespace) | resource |
| [kubernetes_service.mlflow_tracking](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/data-sources/service) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_artifact_azure"></a> [artifact\_azure](#input\_artifact\_azure) | Boolean to indicate if we are using Azure Blob Storage as storage for MLFlow | `bool` | `true` | no |
| <a name="input_artifact_azure_access_key"></a> [artifact\_azure\_access\_key](#input\_artifact\_azure\_access\_key) | Access Key for Azure Blob Storage | `string` | `""` | no |
| <a name="input_artifact_proxied_access"></a> [artifact\_proxied\_access](#input\_artifact\_proxied\_access) | Boolean to indicate if we are using proxied artifact storage | `bool` | `false` | no |
| <a name="input_storage_account_name"></a> [storage\_account\_name](#input\_storage\_account\_name) | Name of Azure Storage Container already created inside Azure Blob Storage | `string` | n/a | yes |
| <a name="input_storage_container_name"></a> [storage\_container\_name](#input\_storage\_container\_name) | Name of container to create inside Azure Storage Account to store artifacts | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_mlflow_tracking_url"></a> [mlflow\_tracking\_url](#output\_mlflow\_tracking\_url) | The tracking URL for MLFlow dashboard |
