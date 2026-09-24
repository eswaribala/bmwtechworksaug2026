API Documentation
=================

The BMW Natural Language Analyst provides a FastAPI application for
submitting natural-language BMW analytics questions.

API Base URL
------------

::

    http://127.0.0.1:8000

Endpoints
---------

Health Check
~~~~~~~~~~~

::

    GET /health

Checks whether the API application is running.

Readiness Check
~~~~~~~~~~~~~~~

::

    GET /ready

Checks whether the application can communicate with Snowflake.

Ask Question
~~~~~~~~~~~~

::

    POST /ask

Example request::

    {
        "question": "Which BMW model had the highest warranty cost in Chennai?"
    }

Example response::

    {
        "question": "Which BMW model had the highest warranty cost in Chennai?",
        "intent": "warranty_cost",
        "sql": "...",
        "data": [
            {
                "MODEL": "BMW i5",
                "TOTAL_WARRANTY_COST": 1136000.0
            }
        ],
        "answer": "BMW i5 had the highest warranty cost in Chennai."
    }

Metrics
~~~~~~~

::

    GET /metrics

Returns application metrics.

Running the API
---------------

::

    python -m uvicorn bmw_analyst.api.main:app --host 127.0.0.1 --port 8000 --reload
