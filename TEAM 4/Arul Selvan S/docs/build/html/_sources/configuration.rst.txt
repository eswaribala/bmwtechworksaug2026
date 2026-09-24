Configuration
=============

Environment configuration is stored in the project's ``.env`` file.

Snowflake Configuration
-----------------------

::

    SNOWFLAKE_ACCOUNT=<account>
    SNOWFLAKE_USER=<user>
    SNOWFLAKE_PASSWORD=<password>
    SNOWFLAKE_AUTHENTICATOR=snowflake
    SNOWFLAKE_ROLE=BMW_ANALYST_READONLY
    SNOWFLAKE_WAREHOUSE=BMW_WH
    SNOWFLAKE_DATABASE=BMW_ANALYTICS
    SNOWFLAKE_SCHEMA=BMW_DATA

Ollama Configuration
--------------------

The BMW Natural Language Analyst uses Ollama for local LLM inference.

::

    OLLAMA_BASE_URL=http://127.0.0.1:11434
    OLLAMA_MODEL=llama3.2:1b

The model is running locally through Ollama and does not require
AWS Bedrock for LLM inference.

Application Configuration
-------------------------

::

    API_HOST=127.0.0.1
    API_PORT=8000

    STREAMLIT_HOST=127.0.0.1
    STREAMLIT_PORT=8501

    MCP_SERVER_NAME=BMW Natural Language Analyst
    APP_NAME=BMW Natural Language Data Analyst
    LOG_LEVEL=INFO

AWS
---

::

    AWS_REGION=ap-south-1

AWS configuration is available for optional AWS integrations.

Secrets
-------

Sensitive credentials should not be committed to Git.

The ``.env`` file should remain excluded through ``.gitignore``.
