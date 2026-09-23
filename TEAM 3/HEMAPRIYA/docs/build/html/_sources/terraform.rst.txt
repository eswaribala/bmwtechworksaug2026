Terraform Infrastructure
=========================

Overview
--------

Terraform is used as Infrastructure as Code (IaC) for the AWS resources
required by the project.

Instead of creating and configuring cloud infrastructure manually,
Terraform describes the required infrastructure in configuration files.

The project currently uses Terraform to manage the Amazon S3 storage
infrastructure.

Infrastructure Flow
-------------------

The infrastructure flow is:

.. code-block:: text

   Terraform Configuration
            |
            v
      Terraform Plan
            |
            v
      Terraform Apply
            |
            v
       AWS Resources
            |
            v
        Amazon S3


Terraform Configuration
-----------------------

The Terraform configuration is located in:

.. code-block:: text

   terraform/
   |
   +-- main.tf
   +-- .terraform/
   +-- terraform.tfstate
   +-- terraform.tfstate.backup


Provider
--------

The project uses the AWS Terraform provider.

The configured AWS region is:

.. code-block:: text

   us-east-1

The AWS provider is defined in ``main.tf``.

S3 Bucket
---------

Terraform manages the project S3 bucket:

.. code-block:: text

   bmw-dealer-inventory-recommendation-2026

The bucket is used to store project data and Athena query results.


Managed Resources
-----------------

The Terraform configuration manages the following S3 resources.

S3 Bucket
~~~~~~~~~

The main S3 bucket is defined using:

.. code-block:: text

   aws_s3_bucket.inventory

The bucket contains tags identifying the project, environment, and
Terraform management.

Bucket Versioning
~~~~~~~~~~~~~~~~~

S3 versioning is enabled using:

.. code-block:: text

   aws_s3_bucket_versioning.inventory

Versioning helps maintain previous versions of objects stored in the
bucket.

Server-Side Encryption
~~~~~~~~~~~~~~~~~~~~~~

Server-side encryption is enabled using:

.. code-block:: text

   aws_s3_bucket_server_side_encryption_configuration.inventory

The configured encryption algorithm is:

.. code-block:: text

   AES256

This provides encryption for objects stored in the S3 bucket.

Public Access Block
~~~~~~~~~~~~~~~~~~~

Public access is blocked using:

.. code-block:: text

   aws_s3_bucket_public_access_block.inventory

The configuration enables:

* Block public ACLs
* Block public bucket policies
* Ignore public ACLs
* Restrict public buckets

This helps prevent accidental public exposure of the project data.


Terraform Workflow
------------------

The normal Terraform workflow is:

.. code-block:: text

   Write Configuration
          |
          v
   terraform fmt
          |
          v
   terraform init
          |
          v
   terraform validate
          |
          v
   terraform plan
          |
          v
   terraform apply


Terraform Init
~~~~~~~~~~~~~~

The ``terraform init`` command initializes the Terraform working
directory and downloads the required provider.

Example:

.. code-block:: console

   terraform init


Terraform Format
~~~~~~~~~~~~~~~~

The ``terraform fmt`` command formats Terraform configuration files.

Example:

.. code-block:: console

   terraform fmt


Terraform Validate
~~~~~~~~~~~~~~~~~~

The ``terraform validate`` command checks whether the Terraform
configuration is syntactically valid and internally consistent.

Example:

.. code-block:: console

   terraform validate


Terraform Plan
~~~~~~~~~~~~~~

The ``terraform plan`` command shows the infrastructure changes that
Terraform intends to make.

Example:

.. code-block:: console

   terraform plan


Terraform Apply
~~~~~~~~~~~~~~~

The ``terraform apply`` command applies the planned infrastructure
changes to AWS.

Example:

.. code-block:: console

   terraform apply


Terraform State
---------------

Terraform maintains state information to track the AWS resources managed
by the configuration.

The project uses:

.. code-block:: text

   terraform.tfstate

The state file should not be committed to Git because it can contain
infrastructure information that is not appropriate for source control.

The project therefore ignores Terraform state files through
``.gitignore``.


Terraform and GitHub Actions
----------------------------

Terraform validation is also included in the GitHub Actions CI workflow.

The CI pipeline performs:

.. code-block:: text

   Git Push / Pull Request
           |
           v
     GitHub Actions
           |
           v
     terraform init
           |
           v
     terraform validate
           |
           v
     terraform fmt -check


This ensures that Terraform configuration remains valid and properly
formatted.


Security
--------

The Terraform configuration includes several security controls for the
S3 bucket.

These include:

* Server-side encryption
* Public access blocking
* Bucket versioning

AWS credentials are not stored in the Terraform source files.

Credentials should be provided through the AWS environment or an
appropriate authenticated AWS mechanism.


Infrastructure Reproducibility
------------------------------

One of the main advantages of Terraform is reproducibility.

Another developer can initialize the Terraform configuration and review
the planned infrastructure using:

.. code-block:: console

   terraform init

   terraform validate

   terraform plan

The configuration therefore acts as a documented definition of the AWS
infrastructure required by the project.


Current Scope
-------------

The current Terraform implementation focuses on the S3 infrastructure
used by the project.

AWS Athena is used for analytics over the S3 data, but Athena resources
are not currently managed by the Terraform configuration.

Future infrastructure improvements may include:

* Athena infrastructure
* IAM roles and policies
* CloudWatch resources
* Additional S3 lifecycle policies
* Automated deployment infrastructure
* Environment-specific configurations