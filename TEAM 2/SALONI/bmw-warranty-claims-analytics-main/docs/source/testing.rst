Testing
=======

The BMW Warranty Claims Analytics project uses automated testing to
verify data validation and transformation logic.

Testing Framework
-----------------

The project uses:

* Python
* pytest
* PySpark

Test Location
-------------

The automated tests are located in:

::

    tests/

Test Files
----------

The project contains the following test files:

``test_validation.py``
~~~~~~~~~~~~~~~~~~~~~~

Tests the warranty claim validation rules, including:

* Valid warranty claims.
* Missing claim IDs.
* Unknown vehicle references.
* Negative claim amounts.
* Invalid claim dates.

``test_transformation.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests the enrichment of valid warranty claims with vehicle master
information.

The enrichment process verifies that vehicle details are correctly
associated with warranty claims.

``test_analytics.py``
~~~~~~~~~~~~~~~~~~~~~

This file is reserved for future Python-based analytics tests.

Analytics are currently implemented using Snowflake SQL views and
queries.

Running the Tests
-----------------

Activate the virtual environment:

::

    .\envwarranty\Scripts\Activate.ps1

Run the complete test suite:

::

    python -m pytest .\tests -v

Run the validation tests only:

::

    python -m pytest .\tests\test_validation.py -v

Run the transformation tests only:

::

    python -m pytest .\tests\test_transformation.py -v

Expected Result
---------------

A successful test execution reports that all implemented tests have
passed.

The test suite verifies the core validation and transformation logic
before the processed data is used for downstream analytics.