MCP
===

The BMW Natural Language Analyst uses the Model Context Protocol (MCP)
to expose BMW analytics tools.

MCP Architecture
-----------------

::

    BMW Analyst Agent
           |
           v
       MCP Client
           |
           v
       MCP Server
           |
           v
        Snowflake

MCP Tools
---------

Vehicle Sales
~~~~~~~~~~~~~

::

    vehicle_sales

Provides BMW vehicle sales information.

Warranty Cost
~~~~~~~~~~~~~

::

    warranty_cost

Provides BMW warranty information and warranty costs.

Fault Summary
~~~~~~~~~~~~~

::

    fault_summary

Provides BMW fault information.

Battery Status
~~~~~~~~~~~~~~

::

    battery_status

Provides BMW battery information.

Approved Query
~~~~~~~~~~~~~~

::

    execute_approved_query

Executes a validated read-only SQL query.

Security
--------

The MCP server validates SQL before allowing execution.

Only approved read-only operations are permitted.

MCP Server
----------

The MCP server can be started using:

::

    python -m bmw_analyst.mcp_server.server

The application normally starts and manages the MCP process through
the MCP client.
