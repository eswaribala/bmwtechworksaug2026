Testing
=======

The BMW Natural Language Analyst uses pytest for automated testing.

Run Tests
---------

Run all non-integration tests:

::

    python -m pytest -q -m "not integration"

Run All Tests
-------------

::

    python -m pytest -q

Test Categories
---------------

API Tests
~~~~~~~~~

Tests FastAPI endpoints and API behavior.

Agent Tests
~~~~~~~~~~~

Tests the BMW analyst agent.

MCP Tests
~~~~~~~~~

Tests MCP client and server behavior.

Router Tests
~~~~~~~~~~~~

Tests natural-language intent routing.

SQL Validator Tests
~~~~~~~~~~~~~~~~~~~

Tests read-only SQL security rules.

Query Limit Tests
~~~~~~~~~~~~~~~~~~

Tests maximum query result limits.

Snowflake Tests
~~~~~~~~~~~~~~~

Tests Snowflake connectivity and execution.

Current Result
--------------

The non-integration test suite currently passes:

::

    60 passed
    2 deselected

The Starlette/AnyIO deprecation warning does not represent a test
failure.
