API
===

FastAPI application
-------------------

The API is implemented in ``src/api/main.py`` and exposes the following
endpoints.

.. list-table::
   :header-rows: 1
   :widths: 25 55

   * - Endpoint
     - Purpose
   * - ``GET /health``
     - Service health check.
   * - ``GET /summary``
     - Overall dashboard metrics.
   * - ``GET /vehicles/top?limit=5``
     - Highest-efficiency vehicles.
   * - ``GET /vehicles/bottom?limit=5``
     - Lowest-efficiency vehicles.
   * - ``GET /models``
     - Model-level efficiency.
   * - ``GET /regions``
     - Region-level efficiency.
   * - ``GET /range-trend``
     - Daily estimated-range trend.

Local data layer
----------------

``src/api/queries.py`` currently reads curated CSV files from
``data/curated_local/``. This keeps the local application independent of
AWS credentials.

For the AWS deployment, the query layer can be replaced with an Athena
implementation while preserving the API route structure.

Python API reference
--------------------

.. automodule:: src.api.main
   :members:
   :undoc-members:

.. automodule:: src.api.queries
   :members:
   :undoc-members:
