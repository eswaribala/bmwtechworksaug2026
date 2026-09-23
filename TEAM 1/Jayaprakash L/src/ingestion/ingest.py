"""CSV ingestion utilities for the EV telemetry pipeline.

The ingestion layer reads the project's telemetry CSV file and parses the
``timestamp`` column as a pandas datetime column. Keeping ingestion small
and deterministic makes it reusable from validation and local workflows.
"""

import pandas as pd

def load_csv(path):
    """Load a telemetry CSV and parse ``timestamp`` as datetime values."""
    return pd.read_csv(path, parse_dates=["timestamp"])
