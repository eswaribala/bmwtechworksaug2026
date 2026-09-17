Getting Started
===============

Prerequisites
-------------

- Python 3.10+
- Java 11+ (required by PySpark)
- Node.js 18+ & npm (frontend only)
- Terraform 1.6+ *(optional — AWS infrastructure deployment)*
- AWS CLI *(optional — only needed for a real AWS account)*

Install dependencies
---------------------

.. code-block:: powershell

   pip install -r requirements.txt

Run the backend API
--------------------

.. code-block:: powershell

   python -m uvicorn backend.app:app --reload --port 8000

The backend starts at ``http://localhost:8000``; check
``http://localhost:8000/health``.

Run the frontend
-----------------

.. code-block:: powershell

   cd frontend
   npm install
   npm run dev

The frontend starts at ``http://localhost:5173``.

Run the pipeline from the CLI
-------------------------------

.. code-block:: powershell

   python src/main.py --dataset telemetry --input data/sample/bmw_telemetry.csv --local

See `howtorun.md <https://github.com>`_ in the repository root for the full
walkthrough, including validating sample CSVs through the UI.

Build this documentation
--------------------------

.. code-block:: powershell

   pip install sphinx sphinx-rtd-theme myst-parser
   cd docs
   .\make.bat html

Open ``docs/_build/html/index.html`` in a browser to view the generated site.
