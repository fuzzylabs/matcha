# Introduction

With Matcha, you'll be up and running with an open source MLOPs environment in Azure, in 10 minutes.

# Getting started

## Set up your environment

First, install Matcha with PIP:

```
pip install matcha
```

Then, authenticate with Azure:

```
az login
```

And provision your base environment:

```
matcha provision experiments training deployment
```

## Run an example training workflow

Clone the examples repository

```
git clone git@github.com:fuzzylabs/matcha-example.git
```

```
cd matcha-example
```

Install dependencies

```
pip install -r requirements.txt
```

The example uses a ZenML pipeline to train a recommender model. We need to set up ZenML, and tell it about our newly-provisioned MLOps environment:

```
zenml init
```

```
matcha export --target=zenml
```

Now, all that's left to do is run our training pipeline:

```
python run.py --train --deploy
```

Once the pipeline completes, you'll have a model endpoint which you can connect to using Curl.

```
curl https://<ENDPOINT>/recommend?user=1
```
