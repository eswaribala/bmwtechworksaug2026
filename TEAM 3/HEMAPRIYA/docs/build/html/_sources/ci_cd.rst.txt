CI/CD Pipeline
==============

Overview
--------

The project uses GitHub Actions to automate continuous integration (CI)
checks.

The current workflow focuses on validating the Python application and
Terraform configuration whenever changes are pushed or a pull request is
created.

Continuous Integration
----------------------

Continuous Integration automatically checks whether new code changes
continue to work with the existing project.

The current CI pipeline performs:

* Repository checkout
* Python environment setup
* Dependency installation
* Automated testing
* Terraform initialization
* Terraform validation
* Terraform formatting validation


GitHub Actions Workflow
-----------------------

The workflow is stored at:

.. code-block:: text

   .github/
   └── workflows/
       └── ci.yml


Workflow Triggers
-----------------

The workflow runs when code is pushed to:

.. code-block:: text

   main
   develop

It also runs when a pull request targets:

.. code-block:: text

   main
   develop


CI Pipeline Flow
----------------

The workflow can be represented as:

.. code-block:: text

   Developer
       |
       v
   Git Push / Pull Request
       |
       v
   GitHub Actions
       |
       v
   Checkout Repository
       |
       v
   Setup Python
       |
       v
   Install Dependencies
       |
       v
   Run Pytest
       |
       v
   Terraform Init
       |
       v
   Terraform Validate
       |
       v
   Terraform Format Check
       |
       v
   CI Result


Python Environment
------------------

The CI workflow uses Python 3.12.

The workflow installs the project dependencies using:

.. code-block:: console

   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install pytest


Automated Tests
---------------

The CI pipeline runs the recommendation test suite using:

.. code-block:: console

   pytest -p no:anyio tests/test_recommendation.py -v

The tests verify:

* Valid recommendations
* Invalid dealers
* Invalid models
* Non-negative recommendation quantities
* Required output fields


Terraform Validation
--------------------

Terraform configuration is also validated automatically.

The workflow initializes Terraform using:

.. code-block:: console

   terraform init

It then validates the configuration using:

.. code-block:: console

   terraform validate

The workflow also checks formatting using:

.. code-block:: console

   terraform fmt -check


CI Success Criteria
-------------------

A successful CI run requires the automated checks to complete without
errors.

The main validation stages are:

.. code-block:: text

   Dependencies
       |
       v
   Tests
       |
       v
   Terraform Init
       |
       v
   Terraform Validate
       |
       v
   Terraform Format Check


Continuous Delivery
-------------------

Continuous Delivery (CD) refers to automatically preparing or deploying
validated application changes to an environment.

The current project does not automatically deploy the application to
AWS through GitHub Actions.

The current implementation focuses on CI validation.

This separation avoids automatically changing AWS infrastructure from
every development push while the project is still under development.


Future CD Architecture
----------------------

A future deployment pipeline could follow:

.. code-block:: text

   Git Push
      |
      v
   GitHub Actions
      |
      v
   Run Tests
      |
      v
   Validate Terraform
      |
      v
   Build Application
      |
      v
   Deployment Approval
      |
      v
   Deploy Infrastructure
      |
      v
   Deploy Application
      |
      v
   Production Environment


Infrastructure Deployment
-------------------------

Terraform can be used as part of a future CD workflow to deploy or
update AWS infrastructure.

Before enabling automated deployment, the workflow should use a secure
AWS authentication mechanism rather than storing long-lived AWS access
keys in the repository.


Security
--------

The CI/CD workflow should not contain:

* AWS access keys
* AWS secret keys
* Passwords
* API keys
* Database credentials

Sensitive configuration should be supplied through secure GitHub Actions
secrets or an appropriate short-lived identity mechanism.


Branch Strategy
---------------

The current CI workflow validates changes on:

* ``main``
* ``develop``

Pull requests targeting these branches are also validated.

This allows code changes to be checked before they are merged.


Benefits
--------

The CI pipeline provides:

* Automated testing
* Consistent validation
* Early detection of errors
* Terraform configuration checks
* Reduced manual verification
* Repeatable development checks


Future Improvements
-------------------

Potential CI/CD improvements include:

* Code coverage reporting
* Static code analysis
* Security scanning
* Dependency vulnerability scanning
* Automated frontend tests
* Docker image build validation
* AWS deployment
* Infrastructure deployment through Terraform
* Environment-specific deployments
* Deployment approval gates
* Post-deployment health checks
* Rollback automation