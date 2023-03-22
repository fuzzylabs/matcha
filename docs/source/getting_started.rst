.. _getting_started:

Getting Started
===============

Getting started with matcha-ml couldn't be simpler, we'll have you up and running in less than 10 minutes. We have a number of examples, see `here <https://github.com/fuzzylabs/matcha-examples>`_ for our repository.

A movie recommender with experiment tracking
############################################

In this example, we'll show you how to use `matcha` to setup a default cloud environment on Azure and hook up a movie recommendation example to run on that example. 

What's the benefit of experiment tracking?
******************************************

If you're reading through our documentation then it's quite likely that we don't need to sell the benefit of tracking your experiments. Even so, it's worth emphasising. Having experiment tracking means that for each run of your pipeline, its metadata is stored in a central place. Importantly, this means that there is a provenance to your model.

Pre-requisties
**************

While matcha-ml is an easy to use tool, it unfortunately can't do everything. Before trying to provision infrastructure on Azure, matcha-ml needs you to be authenticated and to have the correct permissions for the tools you're wanting to deploy. See our explainer on :ref:`Azure permissions <azure_permissions>`.


Getting Setup
*************

Let's start with cloning our examples repository::

    git clone git@github.com:fuzzylabs/matcha-example.git

Move into the recommendation example directory::

    cd recommendation 

Create a virtual environment::

    python3 -m venv venv 
    source venv/bin/activate 

.. note::
    There is a requirement for the Python version being used in this example to be 3.8+. We recommended making use of `pyenv <https://github.com/pyenv/pyenv>`_ to manage your versions.

Install `matcha`::

    pip install matcha-ml 

Test that your installation is working by running::

    matcha --version

The output should be: Matcha version: |version|


Provision your environment with `matcha`
****************************************

Now you have your virtual environment configured and `matcha` is installed, it's now time to provision your environment. For this example, we'll deploy an experiment tracker (MLFlow) to Azure which, when you run the movie recoomender, log the metadata.

To start, you need to authenticate with Azure (see :ref:`Pre-requisties`)::

    az login 

