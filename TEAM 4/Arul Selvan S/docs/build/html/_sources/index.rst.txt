BMW Natural Language Analyst
============================

The BMW Natural Language Analyst allows business users to ask BMW
analytics questions using natural language instead of manually writing
SQL.

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   architecture
   project_structure
   configuration
   mcp
   snowflake
   security
   api
   testing
   terraform

Overview
--------

The application follows this flow:

::

    User
      |
      v
    Llama 3.2 1B / Agent
      |
      v
    MCP Client
      |
      v
    MCP Server
      |
      v
    SQL Validation
      |
      v
    Snowflake
      |
      v
    Result
      |
      v
    Response

Acceptance Question
-------------------

::

    Which BMW model had the highest warranty cost in Chennai?

Expected result:

::

    BMW i5
    Total warranty cost: 1,136,000

Technology Stack
----------------

* Python 3.12
* Ollama
* Llama 3.2 1B
* MCP
* Snowflake
* FastAPI
* Streamlit
* pytest
* Terraform
* Sphinx
