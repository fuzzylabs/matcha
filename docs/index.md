`matcha` is a tool for provisioning MLOps environments to the cloud.

## Why do you need `matcha`?

Many proprietary MLOps platforms try to be an all-in-one solution, taking care of each stage in a machine learning model’s life cycle, from experimentation, to continuous training, deployment, and monitoring. More often than not, these come with vendor lock-in, inflexibility, and suffer from being a _jack of all trades, master of none._

One alternative to this would be to build your own MLOps environment by selecting and combining individual open-source tools. Typically, each of these tools are good at one specific thing, though building a complete pipeline can be complex and time consuming. Broadly, there are a few components which you'll need for an MLOps solution:

* An environment in which to do Machine Learning efficiently.
* The ability to hook that environment up to your ML workflow.
* Knowledge around what best practise looks like for MLOps.

`matcha` seeks to address these, and we want to provide our users with the ability to:

1. Get up and running with an MLOps environment where models can be trained and deployed, using only open source technologies.
2. Link your provisioned MLOps environment to your ML workflow.

## Sensible defaults

The components of the environment that you might want to deploy could differ depending on your workflow. In most cases, however, the environment is broadly the same for most Machine Learning tasks and is usually composed of the following:

* A way to run model training.
* A way to track experiments.
* A way to deploy and serve models.

The current version of `matcha` provisions the above with the single command, using sensible defaults for the infrastructure.

There are more components that could be added here, for example, managing and versioning datasets, the management of models (registration and governance), and monitoring models. Adding all of these is on our roadmap.

## Where do I go from here?

Hopefully we've convinced you just how awesome `matcha` is. Now, you're probably wondering where on earth to go next?

We've got that covered! We have a [getting started](getting-started.md) guide which will show you how to use `matcha` to provision an environment on Azure and then how to use `matcha` to hook that environment up to a pre-built recommendation workflow.
