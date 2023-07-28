# v0.2.7

# 💾 Data Version Control!

A fundamental part of Machine Learning is data, without it the learning part cannot happen, and therefore an important part of any MLOps infrastructure stack. Keeping track of that data and being able to version it is important, it enables the reproduction of experiments.

In this release of Matcha, we've added infrastructure to support data version control as part of our default stack.

You can get the information necessary to hook the infrastructure up to your favorite data version control tool by doing the following:

```python
data_version_control = matcha.get('data-version-control')
```

OR

```bash
matcha get data-version-control
```

## 🐛 Bug Fixes + Improvements
We've also been busy fixing a whole bunch of bugs and improvements:

* [RPD-261] [BUG] destroy leads to missing matcha config file error ([#165](https://github.com/fuzzylabs/matcha/pull/165))
* [RPD-276] [BUG] Turning analytics on causes hanging in the analytics service ([#168](https://github.com/fuzzylabs/matcha/pull/168))
* [RPD-271] [BUG] Fix orphaned NetworkWatcherRG resource group ([#167](https://github.com/fuzzylabs/matcha/pull/167))
* [RPD-279] [BUG] Automatically deal with stale states ([#170](https://github.com/fuzzylabs/matcha/pull/170))
* [RPD-274] [BUG] Fix inaccurate provisioning messages ([#177](https://github.com/fuzzylabs/matcha/pull/177))
* [RPD-263] add inference of zenml version from environment ([#178](https://github.com/fuzzylabs/matcha/pull/178))
* [RPD-272] Updates to documentation ([#166](https://github.com/fuzzylabs/matcha/pull/166))
* [RPD-273] Improvements to the provision user experience ([#173](https://github.com/fuzzylabs/matcha/pull/173))

See all changes here: https://github.com/fuzzylabs/matcha/compare/v0.2.6...v0.2.7

---
# v0.2.6

# 🔌 Matcha as an API!

We've been quietly working away on Matcha and we've re-engineered the core of Matcha to support programmatically deploying infrastructure to Azure.

While you'll still be able to use your favorite commands on the CLI (`matcha get experiment-tracker`), you can now incorporate Matcha into your Python workflows:

```python
experiment_tracker = matcha.get('experiment-tracker')
```

This means that you can stand-up, link tools to their infrastructure, and tear-down resources in a couple of lines of Python code.

See our [new reference documentation](https://mymatcha.ai//references/) to get started!

We're also pleased that as part of this release, we had our first external PR from [Alex](https://github.com/strickvl), a friend of ours over at [ZenML](zenml.io) https://github.com/fuzzylabs/matcha/pull/161.

Date: 19th July 2023

See all changes here: https://github.com/fuzzylabs/matcha/compare/v0.2.5...v0.2.6

---
# v0.2.5

# &#129309; Matcha goes multi-user!

In this version, we're introducing remote state management. What this means is that more than one user can use and interact with Azure resources provisioned using Matcha.

Our goal is to build a tool that is useful and as usable as possible and to understand this, we're also introducing analytics. These analytics enable us to anonymously understand how the tool is being used. We've provided detailed information about this in [our documentation](https://mymatcha.ai/privacy/)

Date: 6th June 2023

## Features

### &#129489;&#8205;&#127891; Remote State Management

Instead of state being managed locally, meaning that only a single user could use Matcha to provision and interact with resources, state is now managed on Azure. For this to work, we're provisioning an additional bucket on Azure to act as a state oracle.

When a set of resources are provisioned, a `matcha.config.json` file will be created - this enables Matcha to communicate with the resources and must be included in your version control to enable resource sharing between users.

How this works under the hood has been described in detail [here](https://mymatcha.ai/inside-matcha/)

### Analytics

We want to make a tool that is both useful and usable. To achieve this, it's important that we understand how the tool is being used by the community.

By collecting fully anonymized usage data, i.e., logging a command being run, it'll enable us to accelerate development and demonstrate value both for us and potential partners.

This version implements that functionality.

We've explained what we're collecting and why in our documentation - see [here](https://mymatcha.ai/privacy/). Users are automatically opted-in to the collection of the usage data, however, we've implemented functionality to opt-out: `matcha analytics opt-out`

See all changes here: https://github.com/fuzzylabs/matcha/compare/v0.2.4...v0.2.5

---
# 0.2.4

&#128293; This version contains a hot fix for matcha get command, so it does not throw an error when run without arguments.

See all changes here: [v0.2.3...v0.2.4](https://github.com/fuzzylabs/matcha/compare/v0.2.3...v0.2.4)

---
# 0.2.3

&#128293; This version contains a quick fix for an import error caused by an old version of `urllib3`

See all changes here: [v0.2.2...v0.2.3](https://github.com/fuzzylabs/matcha/compare/v0.2.2...v0.2.3)

---
# 0.2.2

This release includes documentation changes and bug fixes (detailed below) prior to the public announcement.

Date: 16th May 2023

## Bug Fixes:

* Provisioning failed when the local machine had never previously ran anything related to Kubernetes - fixed (PR https://github.com/fuzzylabs/matcha/pull/86)
* When provisioning failed part way through, `destroy` was unable to deprovision the partially provisioned component stack - fixed (PR https://github.com/fuzzylabs/matcha/pull/88)
* Added `pymdown-extensions` as a dependency to solve security issue - PR https://github.com/fuzzylabs/matcha/pull/99

## Documentation Updates (docs/readme):

* The landing page has been overhauled to improve the narrative and provide a better introduction
* The getting started guide has been updated to improve language and structure
* The README has been updated to include badges and a GIF, along with structural and language changes.

## Other fixes/changes:

* Added attribution to the relevant terraform files

See all changes here: [v0.2.1...v0.2.2](https://github.com/fuzzylabs/matcha/compare/v0.2.1...v0.2.2)

---
# 0.2.1

In this release, we introduce `matcha` to the world - an open source tool for provisioning MLOps environments to the cloud.

With this alpha release of `matcha`, you can provision the infrastructure necessary to enable the following capabilities:

- A way to run model training pipelines
- A way to track experiments
- A way to deploy and serve models

This an alpha version of `matcha` and we're continually working on improvements and adding new features. If you run into any issues, then please report them as [issues](https://github.com/fuzzylabs/matcha/issues) - we really appreciate any feedback.

**How to get started**

To demonstrate practical ways in which you can get started with using `matcha`, see our [workflow examples](https://github.com/fuzzylabs/matcha-examples). Our [documentation](https://fuzzylabs.github.io/matcha/) also provides more information on how `matcha` works, what Azure permissions you need, and much more.

You can install `matcha` using `pip`:

```bash
pip install matcha-ml
```

We hope you enjoy using `matcha` and stay tuned for the next release!
