Testing
=======

Overview
--------

Automated testing is used to verify that the inventory recommendation
system behaves correctly for valid and invalid inputs.

The project uses Pytest for automated testing.

The tests focus primarily on the recommendation engine because it contains
the core business functionality of the application.


Testing Structure
-----------------

The test file is located at:

.. code-block:: text

   tests/
   └── test_recommendation.py


Test Cases
----------

The project contains five automated tests.

Valid Recommendation
~~~~~~~~~~~~~~~~~~~~~

This test verifies that a valid dealer and BMW model produce a
recommendation successfully.

The test checks that the recommendation engine can:

* Accept a valid dealer
* Accept a valid BMW model
* Generate a recommendation
* Return the expected result structure


Invalid Dealer
~~~~~~~~~~~~~~

This test verifies that the system correctly handles a dealer ID that
does not exist.

The recommendation engine should raise a validation error instead of
attempting to generate a recommendation for an unknown dealer.


Invalid Model
~~~~~~~~~~~~~

This test verifies that the system correctly handles a BMW model that
does not exist.

The recommendation engine should reject the invalid model.


Recommended Quantity Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This test verifies that the recommended inventory quantity is never
negative.

The recommendation logic uses a non-negative constraint when calculating
the additional inventory quantity.


Required Output Fields
~~~~~~~~~~~~~~~~~~~~~~

This test verifies that the recommendation response contains all the
required output fields.

The expected fields include:

* Dealer
* Model
* Recommended Quantity
* Predicted Next Month Demand
* Current Inventory
* Target Inventory
* Days of Inventory
* Sales Trend
* Reason


Running Tests
-------------

The tests can be executed from the project root using:

.. code-block:: console

   pytest -p no:anyio tests\test_recommendation.py -v

The ``-v`` option displays detailed information about each test.

The ``-p no:anyio`` option is used in the current Windows development
environment to avoid an environment-specific plugin interaction during
test execution.


Test Result
-----------

The complete recommendation test suite successfully passed.

The result was:

.. code-block:: text

   5 passed in 13.88s


Testing Strategy
----------------

The tests cover both successful and failure scenarios.

The overall testing flow is:

.. code-block:: text

   Valid Input
       |
       v
   Recommendation
       |
       v
   Verify Output


   Invalid Input
       |
       v
   Validation Error
       |
       v
   Verify Error Handling


Business Logic Testing
-----------------------

The tests also verify important business rules.

For example, the recommended inventory quantity must satisfy:

.. code-block:: text

   Recommended Quantity >= 0


This ensures that the recommendation engine never asks a dealer to
stock a negative number of vehicles.


API Testing
-----------

The FastAPI application can also be tested through its automatically
generated Swagger interface.

Swagger is available at:

.. code-block:: text

   http://localhost:8000/docs

The API can be used to test:

* ``GET /health``
* ``GET /options``
* ``POST /recommend``

The Swagger interface is useful for manually verifying request and
response behaviour during development.


Error Scenarios
---------------

Important error scenarios include:

* Invalid dealer
* Invalid BMW model
* Missing or invalid request data
* Backend processing failure
* Model prediction failure
* Data loading failure

The API converts known validation errors into appropriate HTTP responses.


Testing and CI
--------------

The automated tests are also executed through GitHub Actions.

The CI workflow installs the project dependencies and executes:

.. code-block:: console

   pytest -p no:anyio tests/test_recommendation.py -v

This ensures that code changes can be automatically checked before they
are merged.


Future Testing Improvements
---------------------------

Future improvements could include:

* Unit tests for feature engineering
* Unit tests for data validation
* API integration tests
* End-to-end frontend tests
* ML model validation tests
* Data quality tests
* Performance tests
* AWS integration tests
* Test coverage reporting