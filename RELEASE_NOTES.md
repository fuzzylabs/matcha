# 0.2.3

&#128293; This version contains a quick fix for an import error caused by an old version of `urllib3`

See all changes here: [v0.2.2...v0.2.3](https://github.com/fuzzylabs/matcha/compare/v0.2.2...v0.2.3)

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
