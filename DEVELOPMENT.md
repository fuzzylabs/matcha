# Developer Readme

This document contains documentation intended for developers of matcha.

## Terraform configuration for Matcha

The default Terraform module in `src/infrastructure` configures default resources on Azure for matcha. This module is not intended to be run on its own, but to be used by the match CLI tool.

### Modules

This module contains submodules for all the resources necessary for matcha
* Azure Resource Group
* Azure Kubernetes Cluster

### Configuration
* `prefix` -- prefix to use for resources, default: matcha
* `location` -- Azure location to provision in

### Getting started

The module is not intended to be run on its own, but by the matcha CLI tool. However, it is possible to run it without matcha

Initialise terraform module:

```
cd src/infrastructure
terraform init
```

### Provision

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
