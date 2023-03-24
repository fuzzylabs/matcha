# Getting Started

Getting started with `matcha` :tea: couldn't be simpler, we'll have you up and running with a fully provision cloud environment in less than 10 minutes. We have a number of examples, see [here](https://github.com/fuzzylabs/matcha-examples) for our examples respository.


## A movie recommender with experiment tracking

In this example, we'll show you how to use `matcha` to setup a default cloud environment on Azure and hook up a movie recommendation pipeline to run on that environment.

### What's the benefit of experiment tracking?

If you're reading through our documentation, then it's quite likely that we don't need to sell the benefit of tracking your experiments. Even so, it's worth emphasising. Having experiment tracking means that for each run of your pipeline, its metadata is stored in a central place. See our [MLOps Principles](mlops_principles.md) page for more!

### Pre-requisties

While `matcha` is an easy to use tool, it unfortunately can't do everything. Before trying to provision infrastructure on Azure, `matcha` needs to you to be authenticated and to have the correct permissions for the tools you're wanting to deploy. See our explainer on [Azure Permissions](azure_permissions.md).

Alongside this, you need the Azure CLI installed - see [here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) on how to install it

### Getting Setup

Let's start with cloning our examples repository:

```bash
git clone git@github.com:fuzzylabs/matcha-examples.git
```

Move into the recommendation example directory:

```bash
cd recommendation
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

> There is a requirement for the Python version being used in this example to be 3.8+. We recommended making use of [`pyenv`](https://github.com/pyenv/pyenv) to manage your versions.

Install `matcha`:

```bash
pip install matcha-ml
```

Test that your installation is working by running:

```bash
$ match --version
Matcha version: 0.1.0
```

### Provisioning your Azure environment with `matcha`

Now you have your virtual environment configured and `matcha` installed, it's time to provision your Azure environment. For this example, we'll deploy an experimental tracker ([MLflow](https://mlflow.org/)) to Azure. There are other components deployed as part of this, see *HERE (TODO)* for a detailed explanation of what `matcha` is doing.

To start, you need to authenticate with Azure (see [pre-requisties](#pre-requisties)):

```bash
az login
```

`matcha` has a set of sensible defaults for the infrastructure that it'll provision for you - see *HERE (TODO)* for more details.  

To provision an experiment tracker using `matcha` run the following command (you'll be asked a series of questions which helps `matcha` personalised the environment to you):

```bash
matcha provision
```

*TODO* Once `provision` has finished doing it's thing, you can run the following command to inspect what has been provisioned on Azure for you:

```bash
matcha provision inspect
```

You should have some output which is similar to the following:

```bash
OUTPUT
```

### Running your recommender

The environment is provisioned, you've got a movie recommender, and you're hyped and ready to go - we hope.

Running the following command will run the recommendation pipeline locally, but the metadata associated with it (e.g., the RMSE performance metric) will be stored in your deployed experiment tracker:

```bash
matcha run
```