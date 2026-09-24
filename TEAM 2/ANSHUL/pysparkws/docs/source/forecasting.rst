Forecasting
===========

The forecasting component is intentionally separated from the main ETL process so that historical data and production pipeline behavior remain unchanged.

Purpose
-------

This workflow reads the cleaned Parquet dataset and builds a monthly sales view for next-month revenue forecasting.

Process flow
------------

1. Read the cleaned Parquet file.
2. Aggregate sales by model, region, and month.
3. Engineer lag and rolling window features.
4. Train a supervised regression model.
5. Predict next-month revenue by region and model.
6. Save the output as a forecast CSV in the data folder.

Main files
----------

The forecasting implementation is in:

.. code-block:: text

   src/pysparkmodule/forecasting/bmw_sales_forecasting.py

The generated files are saved in:

.. code-block:: text

   src/pysparkmodule/data/bmw_monthly_sales_dataset.csv
   src/pysparkmodule/data/bmw_next_month_forecast.csv

Forecasting output format
-------------------------

The forecast file contains:

- forecast_month
- model
- region
- predicted_revenue
- created_at

Design note
-----------

The forecasting workflow does not overwrite or modify the original ETL output. This keeps the pipeline auditable and makes it easier to maintain and extend.
