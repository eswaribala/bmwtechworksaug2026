Testing
=======

The project uses ``pytest`` with a session-scoped PySpark fixture defined in
``tests/conftest.py``.

Test modules
------------

- ``tests/test_validator.py`` — schema, null, VIN, and date validation rules.
- ``tests/test_duplicates.py`` — duplicate detection semantics.
- ``tests/test_ranges.py`` — numeric range checks.
- ``tests/test_referential_integrity.py`` — foreign-key checks against the
  vehicle master reference dataset.
- ``tests/test_quarantine.py`` — quarantine routing of invalid records.
- ``tests/test_quality_score.py`` — Data Quality Score calculation.

Running the tests
------------------

.. code-block:: powershell

   pytest

.. code-block:: powershell

   pytest --cov=src tests/
