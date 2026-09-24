Architecture
============

End-to-end architecture
------------------------

.. graphviz::

   digraph G {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#eaf2f8", color="#5b9bd5", fontname="Arial"];
       source [label="BMW CSV\nsource files"];
       python [label="Python ingestion\nvalidation + canonicalization"];
       s3 [label="AWS S3\nraw/*"];
       stage [label="Snowflake\nExternal Stage"];
       raw [label="RAW\nsource-aligned tables"];
       rawstream [label="RAW Streams\nCDC metadata"];
       p1 [label="PROC_RAW_TO_STAGING"];
       stg [label="STAGING\nconformed tables"];
       stgstream [label="STAGING Streams\nCDC metadata"];
       p2 [label="PROC_STAGING_TO_ANALYTICS"];
       dims [label="Dimensions\nVehicle / Dealer / Region / Date"];
       facts [label="Facts\nTelemetry / Sales"];
       views [label="Analytics Views\nKPIs"];
       api [label="FastAPI\nread-only API"];
       pyspark [label="Optional PySpark\nprocessed telemetry"];

       source -> python -> s3 -> stage -> raw -> rawstream -> p1 -> stg -> stgstream -> p2;
       p2 -> dims;
       p2 -> facts;
       dims -> views;
       facts -> views;
       views -> api;
       s3 -> pyspark [style=dashed, label="batch path"];
   }

Data flow responsibilities
--------------------------

1. **Python ingestion** validates and canonicalizes files before upload.
2. **S3** provides the durable cloud landing zone.
3. **External stage** exposes the S3 prefix to Snowflake.
4. **COPY INTO** reads files from the stage into RAW tables.
5. **RAW streams** capture new DML changes on RAW.
6. ``PROC_RAW_TO_STAGING`` merges new records into STAGING.
7. **STAGING streams** capture the changes produced in STAGING.
8. ``PROC_STAGING_TO_ANALYTICS`` updates dimensions and facts using ``MERGE``.
9. **Task** schedules the orchestration procedure every five minutes when a
   relevant stream has data.
10. **Analytics views** expose business-facing KPIs.
11. **FastAPI** provides a read-only interface over those views.

Initial versus incremental flow
--------------------------------

Initial processing is intentionally different from incremental processing.
The initial batch is loaded from the external stage, copied to RAW, inserted
into STAGING, and then merged into dimensions and facts. Streams are created
after the initial load so the first batch is not mistaken for CDC.

Incremental processing uses the same S3-to-stage-to-RAW entry point, but the
load is filtered to incremental files. ``FORCE = FALSE`` allows Snowflake to
avoid reloading files it already recognizes as loaded. The resulting RAW
inserts are then captured by streams and propagated through the stored
procedure chain.
