FastAPI
=======

Overview
--------

The FastAPI layer exposes the inventory recommendation functionality as a
REST API.

The API acts as the connection between the React frontend and the
recommendation engine.

The request flow is:

.. code-block:: text

   React Frontend
        |
        | HTTP Request
        v
      FastAPI
        |
        v
   Recommendation Engine
        |
        v
   ML Model + Business Logic
        |
        v
   Recommendation Result
        |
        v
      FastAPI
        |
        | JSON Response
        v
   React Frontend


Application
-----------

The FastAPI application is implemented in:

.. code-block:: text

   src/api/main.py

The application provides endpoints for health checking, retrieving
available dealers and models, and generating inventory recommendations.


API Endpoints
-------------

Health Check
~~~~~~~~~~~~

Endpoint:

.. code-block:: text

   GET /health

Purpose:

Checks whether the API service is running.

Example response:

.. code-block:: json

   {
       "status": "healthy"
   }


Available Options
~~~~~~~~~~~~~~~~~

Endpoint:

.. code-block:: text

   GET /options

Purpose:

Returns the available dealer IDs and BMW models that can be selected by
the user.

Example response:

.. code-block:: json

   {
       "dealers": [
           "D001",
           "D002",
           "D003"
       ],
       "models": [
           "2 Series",
           "3 Series",
           "5 Series"
       ]
   }


Inventory Recommendation
~~~~~~~~~~~~~~~~~~~~~~~~

Endpoint:

.. code-block:: text

   POST /recommend

Purpose:

Generates an inventory recommendation for a selected dealer and BMW
model.

Request body:

.. code-block:: json

   {
       "dealer_id": "D001",
       "model": "2 Series"
   }

The API validates the request and passes the dealer and model to the
recommendation engine.


Response
--------

A successful recommendation request returns JSON containing the
recommendation and supporting information.

Example:

.. code-block:: json

   {
       "Dealer": "D001",
       "Model": "2 Series",
       "Recommended Quantity": 7,
       "Predicted Next Month Demand": 21.44,
       "Current Inventory": 25,
       "Target Inventory": 32.16,
       "Days of Inventory": 35.71,
       "Sales Trend": "Stable",
       "Reason": "Demand is relatively stable, but current inventory is
                  below the calculated target inventory."
   }


Request Validation
------------------

The API uses a Pydantic request model.

The request contains:

.. code-block:: text

   dealer_id
   model

This provides structured validation of incoming JSON requests.


Error Handling
--------------

The API handles different types of failures.

Invalid Dealer or Model
~~~~~~~~~~~~~~~~~~~~~~~

If the requested dealer or model does not exist, the recommendation
engine raises a validation error.

The API returns an HTTP 404 response.

Internal Errors
~~~~~~~~~~~~~~~

Unexpected application errors are caught by the API layer and returned
as HTTP 500 responses.

This prevents internal exceptions from causing an uncontrolled API
failure.


CORS Configuration
------------------

Cross-Origin Resource Sharing is enabled so that the React frontend can
communicate with the FastAPI backend during local development.

The configured development origins include:

.. code-block:: text

   http://localhost:5173
   http://127.0.0.1:5173

The API allows the required HTTP methods and request headers.


Swagger Documentation
---------------------

FastAPI automatically provides interactive API documentation.

When the application is running, the Swagger interface is available at:

.. code-block:: text

   /docs

The Swagger interface allows developers to:

* View available endpoints
* Inspect request schemas
* Enter request parameters
* Execute API requests
* View JSON responses
* Test error responses

This makes API testing easier during development.


Running the API
---------------

From the project root, activate the Python virtual environment and run:

.. code-block:: console

   python -m uvicorn src.api.main:app --reload

The ``--reload`` option automatically reloads the application when source
code changes during development.


Local API Flow
--------------

The local development architecture is:

.. code-block:: text

   Browser
      |
      | React
      v
   localhost:5173
      |
      | POST /recommend
      v
   FastAPI
   localhost:8000
      |
      v
   Recommendation Engine
      |
      +--> Feature Engineering
      |
      +--> XGBoost Model
      |
      +--> Inventory Rules
      |
      v
   JSON Recommendation


Frontend Integration
--------------------

The React frontend sends the selected dealer and model to the
``/recommend`` endpoint.

The backend processes the request and returns the recommendation as JSON.

The frontend then displays the returned values to the user.


API Design Principles
---------------------

The API is designed around the following principles:

* Simple REST endpoints
* JSON request and response format
* Input validation
* Meaningful HTTP status codes
* Separation between API and business logic
* Automatic API documentation
* Clear error handling
* Frontend/backend separation


Future Improvements
-------------------

Potential API improvements include:

* Authentication and authorization
* API rate limiting
* Request logging
* Structured application logging
* Response caching
* Production deployment
* API versioning
* Health checks for dependent services