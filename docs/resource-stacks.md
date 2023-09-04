# Resource Stacks 📚

Machine Learning projects often vary in their size, from small-scale experimentation to large deployments, meaning that the infrastructure requirements also change and scale. For example, the infrastructure stack needed for deploying an LLM may require a GPU or vector database, which aren't usually needed in more general machine learning use-cases.

Matcha accommodates both of these requirements, and currently offers two infrastructure stacks which we'll discuss in more detail here and show how you can get started with either.

> Note: These stacks must be set before provisioning any resources and cannot be change whilst a Matcha deployment exists.

## Available stacks

### DEFAULT

The `DEFAULT` stack. This stack is ideal for generic machine learning training and deployments and a good starting point. It includes:
   * [Azure Kubernetes Service](https://azure.microsoft.com/en-gb/products/kubernetes-service)
   * [ZenML](https://www.zenml.io/home)
   * [Seldon Core](https://www.seldon.io/solutions/open-source-projects/core) (deployment)
   * [MLflow](https://mlflow.org/) (experiment tracking)
   * Data version control storage bucket

This is the stack used in the [getting started page](getting-started.md). Follow the link for more information.

### LLM

The `LLM` stack: This includes everything found within the `DEFAULT` stack with the addition of a vector database - Chroma DB. This stack is modified for the training and deployment of Large Language Models (LLMs).

   * [Azure Kubernetes Service](https://azure.microsoft.com/en-gb/products/kubernetes-service)
   * [ZenML](https://www.zenml.io/home)
   * [Seldon Core](https://www.seldon.io/solutions/open-source-projects/core) (deployment)
   * [MLflow](https://mlflow.org/) (experiment tracking)
   * Data version control storage bucket
   * [Chroma DB](https://www.trychroma.com/) (vector database for document retrieval)


We use this stack for [MindGPT](https://github.com/fuzzylabs/MindGPT), our large language model for mental health question answering.

## How to switch your stack

To switch your stack to the 'DEFAULT' stack, run the following command:

```bash
$ matcha stack set default
```

or for the 'LLM' stack:

```bash
$ matcha stack set llm
```

If no stack is set Matcha will use the 'default' stack.


## Custom stacks

Need an additional module or to remove one? The custom stack is for you.

You can start by adding a module to your stack as follows:

```bash
$ matcha stack add experiment_tracker mlflow
```

```bash
$ matcha stack add <module_type> <flavor>
```

If you want to adapt one of the stacks above you can do this by first setting your stack:

```bash
$ matcha stack set llm
```

then adding/removing a module from the stack

```bash
$ matcha stack remove orchestrator
```

and then Matcha provision the specified resources:

```bash
$ matcha provision
```

### Available Modules

| Module Type          | Flavors | Example Usage (add)                          | Example Usage (remove)                |
|----------------------|---------|----------------------------------------------|---------------------------------------|
| orchestrator         | zenml   | `matcha stack add orchestrator zenml`        | `matcha stack remove orchestrator`    |
| experiment_tracker   | mlflow  | `matcha stack add experiment_tracker mflow`  | `matcha stack remove orchestrator`    |
| data_version_control | dvc     | `matcha stack add data_version_control mflow`| `matcha stack remove data_version_control`|
| deployer             | seldon  | `matcha stack add deployer seldon`           | `matcha stack remove deployer`        |
| vector_database      | chroma  | `matcha stack add vector_database chroma`    | `matcha stack remove vector_database` |

> Note: If you have existing provisioned resources, you must destroy them before adding a new module.

See the [API documentation](references.md) for more information.
