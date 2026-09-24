# BMW Snowflake Incremental Data Warehouse — Sphinx Documentation

This directory contains the project's Sphinx documentation source.

## Build locally

From the repository root:

```powershell
python -m pip install "Sphinx>=7,<9"
sphinx-build -b html docs/sphinx docs/_build/html
```

Open `docs/_build/html/index.html`.

The documentation is intentionally written around the actual implementation:

`Python -> S3 -> Snowflake external stage -> COPY INTO RAW -> RAW Streams -> STAGING -> STAGING Streams -> ANALYTICS -> Task/API`

It also documents the distinction between an external stage (a reference to the
S3 location) and `COPY INTO` (the operation that actually loads rows into
Snowflake tables).
