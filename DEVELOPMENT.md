# Developer Readme

This document contains documentation intended for developers of matcha.

## Developer environment setup

In order to work on the tool as a developer, you'll need to configure your local development environment.

**Pre-requisites**

* Python.
* [Poetry](https://python-poetry.org/).
* [PyEnv](https://github.com/pyenv/pyenv).

**Setup**

First, use PyEnv to install the recommended version of Python:

```bash
pyenv install 3.10.5
pyenv local 3.10.5
```

Next, set up Poetry:

```bash
poetry env use 3.10.5
poetry install
```

Now, you can enter the Poetry shell:

```bash
poetry shell
```

**Pre-commit checks**

Install the git hook scripts

```bash
pre-commit install
```

> The pre-commit checks will run automatically on the changed files after commiting files using `git commit` command.

Optionally, to run the hooks against all of the files, run the following command.

```bash
pre-commit run --all-files
```

**Testing**

With the poetry shell active (see above), you can run all the tests using:

```bash
python -m pytest tests
```

Or specific tests:

```bash
python -m pytest tests/test_cli/test_cli.py
```

**Build Python package**

This will build the Python package and place it into the `dist/` directory.

```bash
poetry build
```

**Serve documentation locally**

```bash
mkdocs serve
```

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

The module is not intended to be run on its own, but by the matcha CLI tool. However, it is possible to run it without matcha.

Pre-requisite: [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli#install-terraform)

Initialise terraform module:

```bash
cd src/matcha_ml/infrastructure
terraform init
```

### Provision

To see what resources will be provisioned:

```bash
terraform plan
```

To provision:

```bash
terraform apply
```

To destroy:

```bash
terraform destroy
```
