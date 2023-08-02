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
| [azurerm_role_assignment.zenmlstorage](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_storage_account.zenmlaccount](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account) | resource |
| [azurerm_storage_container.zenmlstoragecontainer](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_container) | resource |
| [azurerm_storage_account.zenmlaccount](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/storage_account) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aks_principal_id"></a> [aks\_principal\_id](#input\_aks\_principal\_id) | Principal id for aks cluster | `string` | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | The Azure Region in which this resources should be created. | `string` | n/a | yes |
| <a name="input_prefix"></a> [prefix](#input\_prefix) | A prefix used for all resources | `string` | n/a | yes |
| <a name="input_resource_group_name"></a> [resource\_group\_name](#input\_resource\_group\_name) | The resource group name which is used to create the resource group | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_zenml_blobstorage_container_path"></a> [zenml\_blobstorage\_container\_path](#output\_zenml\_blobstorage\_container\_path) | The Azure Blob Storage Container path for storing zenml artifacts |
| <a name="output_zenml_primary_access_key"></a> [zenml\_primary\_access\_key](#output\_zenml\_primary\_access\_key) | ZenML Azure Storage Account - Primary access key |
| <a name="output_zenml_primary_blob_connection_string"></a> [zenml\_primary\_blob\_connection\_string](#output\_zenml\_primary\_blob\_connection\_string) | ZenML Azure Storage Account - Primary Blob service connection string |
| <a name="output_zenml_primary_connection_string"></a> [zenml\_primary\_connection\_string](#output\_zenml\_primary\_connection\_string) | ZenML Azure Storage Account - Primary connection string |
| <a name="output_zenml_secondary_access_key"></a> [zenml\_secondary\_access\_key](#output\_zenml\_secondary\_access\_key) | ZenML Azure Storage Account - Secondary access key |
| <a name="output_zenml_secondary_blob_connection_string"></a> [zenml\_secondary\_blob\_connection\_string](#output\_zenml\_secondary\_blob\_connection\_string) | ZenML Azure Storage Account - Secondary Blob service connection string |
| <a name="output_zenml_secondary_connection_string"></a> [zenml\_secondary\_connection\_string](#output\_zenml\_secondary\_connection\_string) | ZenML Azure Storage Account - Secondary connection string |
| <a name="output_zenml_storage_account_name"></a> [zenml\_storage\_account\_name](#output\_zenml\_storage\_account\_name) | The name of the Azure Storage Account used to store ZenML artifacts. |
| <a name="output_zenml_storage_container_name"></a> [zenml\_storage\_container\_name](#output\_zenml\_storage\_container\_name) | The name of the Azure Storage container used to store ZenML artifacts. |
