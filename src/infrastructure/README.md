# Terraform configuration for Matcha

This module configures default resources on Azure for matcha. This module is not intended to be run on its own, but to be used by the match CLI tool.

## Modules

This module contains submodules for all the resources necessary for matcha
* Azure Resource Group
* Azure Kubernetes Cluster

## Configuration
* `prefix` -- prefix to use for resources, default: matcha
* `location` -- Azure location to provision in

## Getting started

Initialise terraform module:

```
terraform init
```

## Provision

To see what resources will be provisioned:

```
terraform plan
```

To provision:

```
terraform apply
```

To destroy:

```
terraform destroy
```
