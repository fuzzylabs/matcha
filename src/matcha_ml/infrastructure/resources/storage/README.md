## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | 3.48.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | 3.48.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_storage_account.storageaccount](https://registry.terraform.io/providers/hashicorp/azurerm/3.48.0/docs/resources/storage_account) | resource |
| [azurerm_storage_container.storagecontainer](https://registry.terraform.io/providers/hashicorp/azurerm/3.48.0/docs/resources/storage_container) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_location"></a> [location](#input\_location) | The Azure Region in which this resources should be created. | `string` | n/a | yes |
| <a name="input_prefix"></a> [prefix](#input\_prefix) | The prefix which should be used for naming storage account ({prefix}storageacc) and container ({prefix}storagecontainer) | `string` | n/a | yes |
| <a name="input_resource_group_name"></a> [resource\_group\_name](#input\_resource\_group\_name) | The resource group name which is used to create the resource group | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_blobstorage_container_path"></a> [blobstorage\_container\_path](#output\_blobstorage\_container\_path) | The Azure Blob Storage Container path for storing your artifacts |
| <a name="output_primary_access_key"></a> [primary\_access\_key](#output\_primary\_access\_key) | Azure Storage Account - Primary access key |
| <a name="output_primary_blob_connection_string"></a> [primary\_blob\_connection\_string](#output\_primary\_blob\_connection\_string) | Azure Storage Account - Primary Blob service connection string |
| <a name="output_primary_connection_string"></a> [primary\_connection\_string](#output\_primary\_connection\_string) | Azure Storage Account - Primary connection string |
| <a name="output_secondary_access_key"></a> [secondary\_access\_key](#output\_secondary\_access\_key) | Azure Storage Account - Secondary access key |
| <a name="output_secondary_blob_connection_string"></a> [secondary\_blob\_connection\_string](#output\_secondary\_blob\_connection\_string) | Azure Storage Account - Secondary Blob service connection string |
| <a name="output_secondary_connection_string"></a> [secondary\_connection\_string](#output\_secondary\_connection\_string) | Azure Storage Account - Secondary connection string |
| <a name="output_storage_account_name"></a> [storage\_account\_name](#output\_storage\_account\_name) | The name of the Azure Storage Account. |
| <a name="output_storage_container_name"></a> [storage\_container\_name](#output\_storage\_container\_name) | The name of the Azure Storage Container. |
