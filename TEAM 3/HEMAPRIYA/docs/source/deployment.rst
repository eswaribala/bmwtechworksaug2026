Deployment
==========

Overview
--------

The BMW Dealer Inventory Recommendation system consists of a Python
backend, React frontend, machine learning model, and AWS infrastructure.

The current project supports local application execution and AWS-based
data storage and analytics.

Deployment Architecture
-----------------------

The overall deployment structure is:

.. code-block:: text

   User
    |
    v
   React Frontend
    |
    v
   FastAPI Backend
    |
    v
   Recommendation Engine
    |
    +------------------+
    |                  |
    v                  v
   ML Model        Historical Data
                       |
                       v
                    AWS S3
                       |
                       v
                    Athena


Backend Deployment
------------------

The FastAPI backend is located under:

.. code-block:: text

   src/api/main.py

During development, the backend can be started using:

.. code-block:: console

   python -m uvicorn src.api.main:app --reload

The API is available locally on:

.. code-block:: text

   http://localhost:8000


API Documentation
~~~~~~~~~~~~~~~~~

FastAPI automatically provides interactive API documentation at:

.. code-block:: text

   http://localhost:8000/docs

The Swagger interface can be used to test the API endpoints.


Frontend Deployment
-------------------

The React frontend is located under:

.. code-block:: text

   frontend/

During development, the React application runs on:

.. code-block:: text

   http://localhost:5173

The frontend communicates with the FastAPI backend through HTTP requests.


Frontend Container
~~~~~~~~~~~~~~~~~~

The frontend includes a Dockerfile for containerized execution.

The Docker image uses Node.js and exposes port 5173.

The container starts the development server using:

.. code-block:: console

   npm run dev -- --host

Docker support is currently focused on the frontend development
environment.


AWS Deployment
--------------

AWS services are used for cloud data storage and analytics.

The main cloud resources are:

* Amazon S3
* Amazon Athena

Amazon S3 stores the project datasets.

Amazon Athena provides SQL-based analytical queries over the data stored
in S3.


Infrastructure Deployment
-------------------------

AWS infrastructure is managed using Terraform.

The Terraform configuration is located at:

.. code-block:: text

   terraform/

The standard infrastructure workflow is:

.. code-block:: console

   terraform init

   terraform validate

   terraform plan

   terraform apply


S3 Infrastructure
~~~~~~~~~~~~~~~~~

Terraform manages the S3 infrastructure required by the project.

The managed configuration includes:

* S3 bucket
* Bucket versioning
* Server-side encryption
* Public access blocking


Application Deployment Status
-----------------------------

The current implementation is primarily a development and demonstration
deployment.

The system components can be run independently:

.. code-block:: text

   React Frontend
        |
        v
   FastAPI Backend
        |
        v
   Recommendation Engine
        |
        v
   ML Model


Cloud Data Layer
~~~~~~~~~~~~~~~~

The cloud data layer is provided by:

.. code-block:: text

   AWS S3
      |
      v
   AWS Athena


CI/CD
-----

GitHub Actions provides continuous integration.

The CI pipeline validates:

* Python dependencies
* Automated tests
* Terraform configuration
* Terraform formatting

The current CI workflow does not automatically deploy the application to
AWS.

Future automated deployment can be added after the CI pipeline has
successfully validated the changes.


Environment Configuration
-------------------------

The application should use environment-specific configuration rather
than hard-coding sensitive values.

Sensitive values such as:

* AWS credentials
* API keys
* Database passwords
* Authentication secrets

must not be stored in the source code.


Security
--------

The deployment architecture includes several security considerations.

AWS S3
~~~~~~

The S3 bucket uses:

* Server-side encryption
* Public access blocking
* Bucket versioning

Source Control
~~~~~~~~~~~~~~

Sensitive files and environment-specific files are excluded through
``.gitignore``.

Examples include:

.. code-block:: text

   .env
   .aws/
   terraform/.terraform/
   terraform/*.tfstate
   terraform/*.tfstate.*


Deployment Verification
-----------------------

After starting the backend, the health endpoint can be used to verify
that the service is running.

Example:

.. code-block:: text

   GET /health


Expected response:

.. code-block:: json

   {
       "status": "healthy"
   }


The recommendation endpoint can then be tested through Swagger or the
frontend.


Deployment Flow
---------------

The complete development deployment flow is:

.. code-block:: text

   Developer
       |
       v
   Git Repository
       |
       +----------------------+
       |                      |
       v                      v
   GitHub Actions          Terraform
       |                      |
       v                      v
     Tests                 AWS S3
       |                      |
       v                      v
   Validation              Athena
       |
       v
   Application
       |
       +------------------+
       |                  |
       v                  v
     React             FastAPI
       |                  |
       +--------+---------+
                |
                v
             User


Future Production Deployment
----------------------------

A future production architecture could include:

* Containerized FastAPI deployment
* Production React build
* HTTPS
* Authentication and authorization
* AWS IAM least-privilege roles
* CloudWatch monitoring
* Automated CI/CD deployment
* Model versioning
* Model monitoring
* Automated model retraining
* Production database or analytical store
* Load balancing
* Health checks
* Automated rollback

The current implementation intentionally focuses on the working MVP and
demonstration requirements before adding production infrastructure.