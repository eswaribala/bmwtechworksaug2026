Architecture
============

The BMW Natural Language Analyst follows a linear processing architecture:

::

    User
      |
      v
    FastAPI / Streamlit
      |
      v
    BMW Analyst Agent
      |
      v
    Intent Router
      |
      v
    Ollama (Llama 3.2 1B)
      |
      v
    SQL Generation
      |
      v
    SQL Validator
      |
      v
    MCP Client
      |
      v
    MCP Server
      |
      v
    Snowflake
      |
      v
    Query Result
      |
      v
    Narrative Response
      |
      v
    User


Main Components
---------------

User Interface
~~~~~~~~~~~~~~

The application provides a Streamlit interface for business users.

Users can enter natural-language BMW analytics questions, for example:

::

    Which BMW model had the highest warranty cost in Chennai?


API
~~~

FastAPI exposes HTTP endpoints for application integration.

The API receives the user's question and passes it to the
``BMWAnalystAgent`` for processing.


BMW Analyst Agent
~~~~~~~~~~~~~~~~~

The ``BMWAnalystAgent`` coordinates the complete processing flow:

* intent detection
* SQL generation
* SQL validation
* MCP execution
* result processing
* response generation

The agent acts as the central component connecting the user request,
LLM, security layer, MCP layer, and Snowflake.


Intent Router
~~~~~~~~~~~~~

The Intent Router identifies the category of the user's question.

Typical BMW analytical intents include:

* vehicle sales
* warranty cost
* fault summary
* battery status

The detected intent helps classify the user's analytical request.


Ollama
~~~~~~

The application uses Ollama with the ``Llama 3.2 1B`` local model.

The model processes the natural-language question and generates the
SQL required to answer the user's request.


SQL Generation
~~~~~~~~~~~~~~

The SQL Generator converts the user's natural-language question into
a SQL query targeting the approved BMW analytical tables in Snowflake.

The generated SQL is passed to the SQL Validator before execution.


SQL Validator
~~~~~~~~~~~~~

The SQL Validator provides the application's read-only security layer.

All generated SQL must pass validation before it can be executed.

The validator allows approved ``SELECT`` queries and rejects
write or destructive operations such as:

* ``INSERT``
* ``UPDATE``
* ``DELETE``
* ``DROP``
* ``ALTER``
* ``TRUNCATE``
* ``CREATE``
* ``MERGE``
* ``GRANT``
* ``REVOKE``

Only validated SQL is passed to the MCP Client.


MCP Client
~~~~~~~~~~

The MCP Client communicates with the MCP Server using the
Model Context Protocol (MCP).

The client sends the validated analytical request to the MCP Server
for execution.


MCP Server
~~~~~~~~~~

The MCP Server exposes the BMW analytical tools and processes
approved requests.

The available analytical tools include:

* ``vehicle_sales``
* ``warranty_cost``
* ``fault_summary``
* ``battery_status``
* ``execute_approved_query``

The MCP Server communicates with Snowflake to execute the approved
query.


Snowflake
~~~~~~~~~

Snowflake stores the BMW analytical data and executes approved
read-only queries.

The main analytical tables are:

::

    BMW_VEHICLE_SALES
    BMW_WARRANTY
    BMW_FAULTS
    BMW_BATTERY


Query Result
~~~~~~~~~~~~

Snowflake returns the query result to the MCP Server.

The result is then returned through the MCP Client to the
``BMWAnalystAgent``.


Narrative Response
~~~~~~~~~~~~~~~~~~

The BMW Analyst Agent converts the query result into a
business-friendly natural-language response.

For example:

::

    The BMW i5 had the highest warranty cost in Chennai,
    with a total warranty cost of INR 11,36,000.

The final response is returned to the user.


Security
--------

Security is applied before SQL execution.

The processing sequence is:

::

    User Question
          |
          v
    SQL Generation
          |
          v
    SQL Validation
          |
          v
    Approved SQL
          |
          v
    MCP Execution
          |
          v
    Snowflake


Only read-only approved queries are allowed to reach Snowflake.
