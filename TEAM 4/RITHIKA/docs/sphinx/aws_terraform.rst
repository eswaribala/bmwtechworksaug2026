AWS and Terraform
=================

AWS responsibilities
--------------------

The AWS side provides the landing zone and the IAM trust required for
Snowflake to read the S3 objects.

The intended resources are:

* S3 bucket for raw data.
* S3 versioning.
* S3 server-side encryption.
* Public-access block.
* IAM policy granting bucket/object read access for Snowflake and pipeline
  write access where required.
* IAM role trusted by the Snowflake-provisioned IAM user using the Snowflake
  external ID.
* CloudWatch log group for platform/pipeline logs.

Terraform layout
----------------

The ``terraform/`` folder defines the AWS provider, S3 bucket, security
controls, CloudWatch log group, IAM policy and Snowflake role. Variables include
AWS region, project/environment names, bucket name, Snowflake IAM user ARN and
Snowflake external ID.

The Snowflake IAM user ARN and external ID are **outputs of Snowflake**, not
values that should be invented locally. Obtain them with:

.. code-block:: sql

   DESC STORAGE INTEGRATION BMW_S3_INTEGRATION;

Use the returned ``STORAGE_AWS_IAM_USER_ARN`` and
``STORAGE_AWS_EXTERNAL_ID`` in the trust policy.

Terraform execution
-------------------

From the ``terraform`` directory:

.. code-block:: powershell

   terraform init
   terraform fmt -recursive
   terraform validate
   terraform plan
   terraform apply

Always inspect the plan before applying. An existing S3 bucket, policy or log
group should not be destroyed just because Terraform state or source files
were reorganized.

Current environment note
------------------------

In the working capstone environment, the S3 bucket used by the project is
``snowflake-data-warehousing-dev-data`` in ``eu-north-1``. A custom IAM role
named ``vrr-snowflake-capstone`` was also created during the implementation.
The Snowflake storage integration must reference the exact role ARN of the
current deployment.

Snowflake trust relationship
-----------------------------

The trust policy answers **who may assume the role**. The S3 permission policy
answers **what that assumed role may do**.

The trust policy should conceptually contain:

.. code-block:: json

   {
     "Effect": "Allow",
     "Principal": {
       "AWS": "<STORAGE_AWS_IAM_USER_ARN>"
     },
     "Action": "sts:AssumeRole",
     "Condition": {
       "StringEquals": {
         "sts:ExternalId": "<STORAGE_AWS_EXTERNAL_ID>"
       }
     }
   }

For S3 reads, the policy should include at least:

* ``s3:GetBucketLocation``
* ``s3:ListBucket``
* ``s3:GetObject``
* ``s3:GetObjectVersion``

The project also includes ``s3:PutObject`` for pipeline writes where required.

Storage integration validation
------------------------------

Before loading the warehouse, validate the connection:

.. code-block:: sql

   SELECT SYSTEM$VALIDATE_STORAGE_INTEGRATION(
     'BMW_S3_INTEGRATION',
     's3://snowflake-data-warehousing-dev-data/raw/telemetry/',
     'telemetry_initial.csv',
     'read'
   );

A successful validation confirms that Snowflake can use the role to access the
specified S3 object.
