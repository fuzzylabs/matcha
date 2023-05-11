<h1 align="center">
    <code>`matcha`</code> &#127861;
</h1>

<p align="center">
    <a href="https://github.com/fuzzylabs/matcha/actions/workflows/ci.yml">
        <img alt="Build" src="https://img.shields.io/github/actions/workflow/status/fuzzylabs/matcha/ci.yml">
    </a>
    <a href="https://github.com/fuzzylabs/matcha/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/github/license/fuzzylabs/matcha?color=blue">
    </a>
</p>




Welcome to `matcha`, the open source tool for provisioning MLOps environments to the cloud.

Data Scientists and practitioners build ML pipelines and productionize them with the following capabilities:

* A way to run model training pipelines
* A way to track experiments
* A way to deploy and serve models

The current version of `matcha` provisions the above with a single command, using sensible defaults for the infrastructure.

More components could be added here, for example, managing and versioning datasets, managing models (registration and governance), and monitoring models. Adding all of these is on our roadmap.

`matcha` uses open source to solve this problem.

By default, `matcha` will `provision` an MLOps environment to Azure with sensible defaults - enough for you to get going with cloud-based training and deployment. From there, you can use `matcha` to `get` information about your provisioned environment.

Please see the following for more information, including install instructions, documentation, and how you can contribute to `matcha`:

* [Getting Started](https://fuzzylabs.github.io/matcha/getting-started/)
* [Documentation](https://fuzzylabs.github.io/matcha/)
* [Contributing](CONTRIBUTING.md)

## Licence

This library is released under the Apache License. See [LICENSE](LICENSE).
