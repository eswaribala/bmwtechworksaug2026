Project Structure
=================

The project is organized as follows:

::

    bmw-natural-language-analyst/
    |
    +-- config/
    |   +-- __init__.py
    |   +-- settings.py
    |
    +-- src/
    |   +-- bmw_analyst/
    |       +-- agent/
    |       +-- api/
    |       +-- mcp_client/
    |       +-- mcp_server/
    |       +-- models/
    |       +-- security/
    |       +-- snowflake/
    |
    +-- tests/
    |   +-- test_api.py
    |   +-- test_agent.py
    |   +-- test_mcp_client.py
    |   +-- test_mcp_tools.py
    |   +-- test_router.py
    |   +-- test_sql_validator.py
    |   +-- test_query_limits.py
    |   +-- test_snowflake.py
    |
    +-- ui/
    |   +-- streamlit_app.py
    |
    +-- data/
    |   +-- sample/
    |
    +-- terraform/
    |   +-- snowflake/
    |
    +-- docs/
    |   +-- source/
    |
    +-- .env
    +-- .gitignore
    +-- pyproject.toml
    +-- requirements.txt
    +-- run.py
    +-- README.md

Agent
-----

The ``agent`` package contains:

* ``agent.py``
* ``router.py``
* ``sql_generator.py``
* ``prompts.py``

MCP
---

The ``mcp_client`` and ``mcp_server`` packages implement MCP
communication.

Snowflake
---------

The ``snowflake`` package contains connection, execution and query
logic.

Security
--------

The ``security`` package contains SQL validation, permissions and
logging configuration.

Tests
-----

The ``tests`` directory contains unit and integration tests.
