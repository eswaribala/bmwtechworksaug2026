Security
========

Security is a core requirement of the BMW Natural Language Analyst.

Read-Only SQL
-------------

The application only permits approved read-only SQL.

Allowed
~~~~~~~

::

    SELECT

Blocked Commands
~~~~~~~~~~~~~~~~

The following commands are blocked:

* INSERT
* UPDATE
* DELETE
* DROP
* ALTER
* TRUNCATE
* CREATE
* MERGE
* GRANT
* REVOKE

Approved Tables
---------------

::

    BMW_VEHICLE_SALES
    BMW_WARRANTY
    BMW_FAULTS
    BMW_BATTERY

Query Limits
------------

Maximum returned rows:

::

    1000

Query timeout:

::

    30 seconds

Question Limit
--------------

Maximum question length:

::

    1000 characters

Snowflake Role
--------------

The application should use the read-only role:

::

    BMW_ANALYST_READONLY

Credentials
-----------

Passwords, API keys and other secrets must not be committed to Git.

The ``.env`` file should be excluded using ``.gitignore``.
