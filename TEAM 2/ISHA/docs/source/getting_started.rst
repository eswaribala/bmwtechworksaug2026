Getting Started
===============

This project can be set up and run locally in a few steps.

Prerequisites
-------------

Before running the pipeline, make sure you have:

- Python 3.10 or later
- a virtual environment
- AWS CLI configured with valid credentials
- access to the required AWS services

Installation
------------

Install the project dependencies:

.. code-block:: bash

   python -m pip install -U pip
   pip install -r requirements.txt

If the project is managed with Poetry or Hatch, use the project configuration accordingly.

Run the ETL Pipeline
--------------------

From the project root, run:

.. code-block:: bash

   python src/cmodule/etl.py

This generates the processed datasets used for the analytics workflow.

Deploy Infrastructure
---------------------

Move to the Terraform directory and initialise the project:

.. code-block:: bash

   cd terraform
   terraform init
   terraform validate
   terraform plan
   terraform apply

This provisions the necessary S3 and Athena resources for the project.

Build the Documentation
-----------------------

To rebuild the Sphinx documentation locally:

.. code-block:: bash

   cd docs
   python -m sphinx -b html source build/html

The generated HTML files will be available in the `build/html` directory.
