Terraform
=========

The project contains Terraform configuration under:

::

    terraform/snowflake/

Purpose
-------

Terraform can be used to define and manage infrastructure required by
the BMW analytics platform.

Infrastructure
--------------

The Terraform configuration is intended to support infrastructure
deployment in a repeatable and version-controlled way.

State
-----

Terraform state files must not be committed to Git.

Sensitive Values
----------------

Credentials and sensitive infrastructure values must be stored
securely and must not be committed to the repository.
