# Deploying your first model with Matcha

In this guide, we'll walk you through how to provision your first machine learning infrastructure to Azure, and then use that infrastructure to train and deploy a model.

The model we're using in this guide is a movie recommender. We picked this because it's one that's quick to get up and running for beginners. The movie recommender is one of a number of example workflows that we've made available on Github. You can view all our examples [here](https://github.com/fuzzylabs/matcha-examples).

# Pre-requisites

## An Azure cloud environment

Matcha uses Azure to provision your infrastructure, so first you'll need to have set up a [Microsoft® Azure account](https://azure.com).

## Tools you'll need

Before diving into this guide, you'll need to install a couple of other things.

* Python 3.8 or newer, along with Virtual Env and PIP.
* The Azure command line tool. Instructions on installing this can be found [here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).
* Terraform. We use this to provision services inside Azure. You'll find installation instructions for your platform [here](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform). We recommend version 1.4 or newer.

# The movie recommender

Matcha has an [examples repository](https://github.com/fuzzylabs/matcha-examples) on Github, and that's what we'll be working from in this guide. There are a number of different examples in that repository, but we'll focus on the movie recommender example. Note, however, that all the examples have been designed to work in much the same way as this one.

Start by cloning the examples repository:

```bash
git clone https://github.com/fuzzylabs/matcha-examples.git
```

Then, enter the `recommendation` directory and set up your Python environment:

```bash
cd recommendation
python3 -m venv venv
source venv/bin/activate
```

Now, let's install Matcha:

```bash
pip install matcha-ml
```

You can test that your installation is working by running

```bash
matcha --version
```

Which should reply with something like `Matcha version: <version number>`.

Now you're ready to provision your infrastructure.

# Provisioning

Using the Azure CLI, you will need to authenticate:

```bash
az login
```

> Note: you'll need certain permissions in order for Matcha to work. If you're unsure, you can just run Matcha and it will tell you if you're missing any permissions. For specifics around permissions, please see our explainer on [Azure Permissions](azure-permissions.md).

Next, let's provision:

```bash
matcha provision
```

Initially, Matcha will ask you a few questions about how you'd like your infrastructure to be set up. Specifically, it will ask for a _name_ for your infrastructure, a _region_ to deploy it to, and a password. After that, it will go ahead of provision infrastructure.

> Note: provisioning can take up to 20 minutes.

Once provisioning is completed, you can query Matcha, using the `get` command:

```bash
matcha get
```

You should have something similar to the following output:

```bash
Cloud
   - flavor: azure
   - resource-group-name: example-resources

Container registry
   - flavor: azure
   - registry-name: crexample
   - registry-url: <url>

Experiment tracker
   - flavor: mlflow
   - tracking-url: <url>

Model deployer
   - flavor: seldon
   - base-url: <url>
   - workloads-namespace: matcha-seldon-workloads

Orchestrator
   - flavor: aks
   - k8s-context: terraform-example-k8s

Pipeline
   - flavor: zenml
   - connection-string: ********
   - server-password: ********
   - server-url: <url>
   - server-username: ********
   - storage-path: az://<path>
```

You can also use `get` to inspect specific resources, for example:

```bash
matcha get experiment-tracker
```

With the following output:

```bash
Below are the resources provisioned.

Experiment tracker
   - flavor: mlflow
   - tracking-url: <url>
```

> Note: You can also get these outputs in either json or YAML format using the following: `matcha get --output json`

By default, Matcha will hide sensitive resource properties. If you need one of these properties, then you can add the `--show-sensitive` flag to your `get` command.

# Training a model

To train the model, you need to do two things.

## Setting up

Before training the model, you'll need to configure your workflow with the provisioned resources. We've written a bash script which automatically gets all the information needed to do the setup and links it to the recommendation workflow:

```bash
./setup.sh
```

> Note: You could do this yourself manually by making use of the `matcha get` command.

## Training

Once `setup.sh` has finished, do the following to train your recommendation model using the resources you've provisioned:

```bash
python run.py --train
```

From here, you'll be able to visit your experiment tracker and see the runs stored there.

# Destroying

The final thing you'll want to do is decomission the infrastructure that Matcha has set up during this guide. Matcha includes a `destroy` command which will remove everything that has been provisioned, which avoids running up an Azure bill!

```bash
matcha destroy
```
