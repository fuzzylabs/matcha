## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.14.8 |
| <a name="requirement_htpasswd"></a> [htpasswd](#requirement\_htpasswd) | 1.0.4 |
| <a name="requirement_kubectl"></a> [kubectl](#requirement\_kubectl) | 1.14.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | n/a |
| <a name="provider_helm"></a> [helm](#provider\_helm) | n/a |
| <a name="provider_kubernetes"></a> [kubernetes](#provider\_kubernetes) | n/a |
| <a name="provider_random"></a> [random](#provider\_random) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_mysql_flexible_database.db](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mysql_flexible_database) | resource |
| [azurerm_mysql_flexible_server.mysql](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mysql_flexible_server) | resource |
| [azurerm_mysql_flexible_server_configuration.require_ssl](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mysql_flexible_server_configuration) | resource |
| [azurerm_mysql_flexible_server_firewall_rule.allow_IPs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mysql_flexible_server_firewall_rule) | resource |
| [helm_release.zen_server](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/resources/release) | resource |
| [kubernetes_namespace.zen_server](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/resources/namespace) | resource |
| [random_password.mysql_password](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/password) | resource |
| [kubernetes_service.zen_server](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/data-sources/service) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_analytics_opt_in"></a> [analytics\_opt\_in](#input\_analytics\_opt\_in) | The flag to enable/disable analytics | `bool` | `false` | no |
| <a name="input_database_password"></a> [database\_password](#input\_database\_password) | The password for the CloudSQL store | `string` | `""` | no |
| <a name="input_database_ssl_ca"></a> [database\_ssl\_ca](#input\_database\_ssl\_ca) | The server ca for the Flexible MySQL instance | `string` | `""` | no |
| <a name="input_database_ssl_cert"></a> [database\_ssl\_cert](#input\_database\_ssl\_cert) | The client cert for the Flexible MySQL instance | `string` | `""` | no |
| <a name="input_database_ssl_key"></a> [database\_ssl\_key](#input\_database\_ssl\_key) | The client key for the Flexible MySQL instance | `string` | `""` | no |
| <a name="input_database_ssl_verify_server_cert"></a> [database\_ssl\_verify\_server\_cert](#input\_database\_ssl\_verify\_server\_cert) | Should SSL be verified? | `bool` | `false` | no |
| <a name="input_database_url"></a> [database\_url](#input\_database\_url) | The URL for the Flexible MySQL instance | `string` | `""` | no |
| <a name="input_database_username"></a> [database\_username](#input\_database\_username) | The username for the CloudSQL store | `string` | `"user"` | no |
| <a name="input_db_disk_size"></a> [db\_disk\_size](#input\_db\_disk\_size) | The allocated storage in gigabytes | `number` | `20` | no |
| <a name="input_db_instance_name"></a> [db\_instance\_name](#input\_db\_instance\_name) | The name for the Flexible MySQL store | `string` | `"zenmlserver"` | no |
| <a name="input_db_name"></a> [db\_name](#input\_db\_name) | The name for the database | `string` | `"zendb"` | no |
| <a name="input_db_sku_name"></a> [db\_sku\_name](#input\_db\_sku\_name) | The sku\_name for the database resource | `string` | `"B_Standard_B1s"` | no |
| <a name="input_db_version"></a> [db\_version](#input\_db\_version) | The version of MySQL to use | `string` | `"5.7"` | no |
| <a name="input_deploy_db"></a> [deploy\_db](#input\_deploy\_db) | Should a Flexible MySQL instance be created? | `bool` | `true` | no |
| <a name="input_kubectl_config_path"></a> [kubectl\_config\_path](#input\_kubectl\_config\_path) | The path to the kube config | `string` | `""` | no |
| <a name="input_location"></a> [location](#input\_location) | The location for your Azure resources | `string` | n/a | yes |
| <a name="input_namespace"></a> [namespace](#input\_namespace) | The namespace to install the ZenML server Helm chart in | `string` | `"terraform-server"` | no |
| <a name="input_password"></a> [password](#input\_password) | Password for the default ZenML server account | `string` | n/a | yes |
| <a name="input_prefix"></a> [prefix](#input\_prefix) | A prefix used for all resources | `string` | n/a | yes |
| <a name="input_resource_group_name"></a> [resource\_group\_name](#input\_resource\_group\_name) | The resource group in Azure that you want to deploy ZenML to | `string` | n/a | yes |
| <a name="input_username"></a> [username](#input\_username) | Username for the default ZenML server account | `string` | `"default"` | no |
| <a name="input_zenmlserver_image_repo"></a> [zenmlserver\_image\_repo](#input\_zenmlserver\_image\_repo) | The repository to use for the zenmlserver docker image. | `string` | `"zenmldocker/zenml-server"` | no |
| <a name="input_zenmlserver_image_tag"></a> [zenmlserver\_image\_tag](#input\_zenmlserver\_image\_tag) | The tag to use for the zenmlserver docker image. | `string` | `"latest"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_zenserver_password"></a> [zenserver\_password](#output\_zenserver\_password) | The password used to access the ZenML server |
| <a name="output_zenserver_url"></a> [zenserver\_url](#output\_zenserver\_url) | The URL for the ZenML server |
| <a name="output_zenserver_username"></a> [zenserver\_username](#output\_zenserver\_username) | The username used to access the ZenML server |
