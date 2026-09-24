Installation
============

Requirements
------------

* Windows
* Python 3.12
* Python virtual environment
* Ollama
* Snowflake account
* Git

Create Virtual Environment
--------------------------

::

    python -m venv bmwvenv

Activate Environment
--------------------

PowerShell::

    .\bmwvenv\Scripts\Activate.ps1

Install Project
---------------

::

    python -m pip install -e ".[dev]"

Verify Installation
-------------------

::

    python -c "import bmw_analyst; print('BMW Analyst import successful')"

Configure Environment
---------------------

Create the project ``.env`` file and configure the required Snowflake,
Ollama, API and application settings.

Run Tests
---------

::

    python -m pytest -q -m "not integration"

Run FastAPI
-----------

::

    python -m uvicorn bmw_analyst.api.main:app --host 127.0.0.1 --port 8000 --reload

Run Streamlit
-------------

::

    streamlit run ui\streamlit_app.py
