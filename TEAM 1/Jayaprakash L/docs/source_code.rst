Source code reference
=====================

The following pages are generated from Python module docstrings. The
docstrings and comments are intentionally kept in the implementation so
the source code remains self-documenting.

Ingestion
---------

.. automodule:: src.ingestion.ingest
   :members:
   :undoc-members:

.. automodule:: src.ingestion.upload_to_s3
   :members:
   :undoc-members:

Validation
----------

.. automodule:: src.validation.validate
   :members:
   :undoc-members:

AWS helpers
-----------

.. automodule:: src.aws.s3
   :members:
   :undoc-members:

PySpark
-------

.. automodule:: src.pyspark.spark_session
   :members:
   :undoc-members:

.. automodule:: src.pyspark.transform
   :members:
   :undoc-members:

.. automodule:: src.pyspark.aggregations
   :members:
   :undoc-members:

.. automodule:: src.pyspark.ranking
   :members:
   :undoc-members:

.. automodule:: src.pyspark.pipeline
   :members:
   :undoc-members:

Tests
-----

.. literalinclude:: ../tests/test_validation.py
   :language: python
   :linenos:

Local runner
------------

.. literalinclude:: ../scripts/run_local_pipeline.py
   :language: python
   :linenos:

Dashboard
---------

.. literalinclude:: ../src/dashboard/app.py
   :language: python
   :linenos:
