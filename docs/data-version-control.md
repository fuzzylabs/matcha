# Data Version Control

One of the resources that matcha provisions by default is a storage container for data. The storage container is
tool-agnostic, so whether you want to use the `dvc` package, `LakeFS` or some other data version control package is 
up to you.

You can find all the specifications for the data version control resource in the 
`infrastructure/data_version_control_storage` folder inside `matcha_ml`.

## Using the provisioned resources with the `dvc` package
Let's work through a short example of provisioning a set of resources using matcha, then setting up data version control
with the popular `dvc` package such that it versions and stores data on the provisioned resources.
The documentation for the `dvc` package can be found [here](https://dvc.org/doc).

First, let's provision a set of resources:

    $ matcha provision

Once that's finished, we can ask matcha for the connection string to our storage bucket.

    $ matcha get --show-sensitive data-version-control

This will print something like the following to your terminal:

    Below are the resources provisioned.
    Data version control
        - flavor: FLAVOR
        - connection-string: CONNECTION_STRING
        - account-name: ACCOUNT_NAME
        - container-name: CONTAINER_NAME

Now that we have our connection string (you should keep this a secret), assuming you have followed the steps from the 
dvc docs for initializing and adding files for `dvc` to track, we can tell the `dvc` package where to look for historic 
data, and where to push new, versionable data. This is done as below:

    $ dvc remote modify --local my_dvc connection_string CONNECTION_STRING
    $ dvc remote modify my_dvc url azure://CONTAINER_NAME
    $ dvc remote modify my_dvc account_name STORAGE_ACCOUNT_NAME

It's important to make sure your connection string is stored in `config.local`, so your connection string never appears 
in any public repository.

That's it! Whenever you run `dvc push`, `dvc pull` or `dvc checkout`, you or whoever you grant access to your storage
container is interacting with the azure storage container provisioned by matcha specifically for data version control.
