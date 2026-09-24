Snowflake
=========

Snowflake is the analytical data platform used by the BMW Natural
Language Analyst.

Database
--------

::

    BMW_ANALYTICS

Schema
------

::

    BMW_DATA

Warehouse
---------

::

    BMW_WH

Tables
------

BMW Vehicle Sales
~~~~~~~~~~~~~~~~~

::

    BMW_VEHICLE_SALES

BMW Warranty
~~~~~~~~~~~~

::

    BMW_WARRANTY

BMW Faults
~~~~~~~~~~

::

    BMW_FAULTS

BMW Battery
~~~~~~~~~~~

::

    BMW_BATTERY

Connection
----------

The application reads Snowflake configuration from environment
variables.

The Snowflake connection uses:

* account
* user
* password
* authenticator
* role
* warehouse
* database
* schema

Connection Reuse
----------------

The application maintains a reusable Snowflake connection to reduce
connection startup overhead.

Query Execution
---------------

Queries are executed through the Snowflake executor after SQL security
validation.

Example
-------

::

    SELECT
        MODEL,
        SUM(WARRANTY_COST) AS TOTAL_WARRANTY_COST
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    WHERE CITY = 'Chennai'
    GROUP BY MODEL
    ORDER BY TOTAL_WARRANTY_COST DESC
    LIMIT 1

Expected result::

    BMW i5
    1136000.0
