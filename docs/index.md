
`matcha` :tea: is your one-stop-shop for efficiently provisioning MLOps tooling and for well-structured ML workflows.

# Introduction

With Matcha, you'll be up and running with an open source MLOPs environment in Azure, in 10 minutes.

# Getting started

## Set up your environment

```
git clone git@github.com:fuzzylabs/matcha-example.git
```

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
# sets up the basic env with sensible defaults
matcha provision
```

## Run an example training workflow

```
cd recommender
```

```
matcha run train deploy
```

Verify that it works

```
matcha verify
```
<!-- # Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files. -->
