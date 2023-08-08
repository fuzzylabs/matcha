# Resource Stacks 📚🧰🏭

Within Matcha we currently offer two sets of resources:

1. The `DEFAULT` stack. This stack is ideal for generic machine learning training and deployments and a good starting point. It includes:
   * Azure Kubernetes Service
   * ZenML
   * Seldon (deployment)
   * MLflow (experiment tracking)
   * Data Version Control storage
2. The `LLM` stack: This includes everything found within the `DEFAULT` stack with the addition of a vector database - Chroma DB. This stack is modified for the training and deployment of Large Language Models (LLMs).

These stacks must be set before provisioning any resources and cannot be changed whilst in deployment.

This can be done by running the following command:

```bash
$ matcha stack set default
```

or

```bash
$ matcha stack set llm
```

for the default and LLM stacks respectively.

If no stack is set Matcha will use the 'default' stack.
