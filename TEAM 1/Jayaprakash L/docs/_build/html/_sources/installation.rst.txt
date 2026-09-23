Installation and execution
==========================

Prerequisites
-------------

* Python 3.10+ recommended.
* Java runtime compatible with the installed PySpark version for local Spark.
* AWS CLI for AWS deployment/testing.
* An AWS account with permissions for S3, Glue, Athena, and IAM when using
  the cloud path.

Create a virtual environment
----------------------------

Windows PowerShell:

.. code-block:: powershell

   python -m venv .venv
   .venv\Scripts\Activate.ps1

Windows CMD:

.. code-block:: bat

   python -m venv .venv
   .venv\Scripts\activate

Linux/macOS:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate

Install project dependencies
----------------------------

.. code-block:: bash

   pip install -r requirements.txt

Run the local pipeline
----------------------

.. code-block:: bash

   python scripts/run_local_pipeline.py

This creates curated CSV files under ``data/curated_local/``.

Run the FastAPI service
-----------------------

.. code-block:: bash

   uvicorn src.api.main:app --reload

The interactive API documentation is then available from the FastAPI
development server.

Run the Streamlit dashboard
---------------------------

.. code-block:: bash

   streamlit run src/dashboard/app.py

Run tests
---------

.. code-block:: bash

   pytest -q

Environment configuration
-------------------------

Copy ``.env.example`` to ``.env`` and provide the AWS values required by
the S3 helper. Do not commit real credentials or secrets.

Build this Sphinx documentation
--------------------------------

Install Sphinx and the HTML theme:

.. code-block:: bash

   pip install sphinx sphinx-rtd-theme

From the project root:

.. code-block:: bash

   sphinx-build -b html docs docs/_build/html

Open the generated documentation:

Windows:

.. code-block:: powershell

   start docs\_build\html\index.html

Linux:

.. code-block:: bash

   xdg-open docs/_build/html/index.html

macOS:

.. code-block:: bash

   open docs/_build/html/index.html

Live-reload development
-----------------------

For automatic rebuilds while editing documentation:

.. code-block:: bash

   pip install sphinx-autobuild
   sphinx-autobuild docs docs/_build/html

Then open the local URL printed by the command.
