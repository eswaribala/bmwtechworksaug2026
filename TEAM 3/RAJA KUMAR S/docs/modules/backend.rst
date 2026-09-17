Backend API
===========

FastAPI service that bridges the frontend CSV upload to the full pipeline:
receives a file via ``POST /upload``, uploads it to S3, runs the data
quality engine, saves curated/quarantine/report artifacts, and returns the
quality report JSON.

.. automodule:: backend.app
   :members:
   :undoc-members:
   :show-inheritance:
