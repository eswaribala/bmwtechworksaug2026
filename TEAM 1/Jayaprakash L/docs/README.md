# Sphinx documentation

## 1. Install

From the project root:

```bash
pip install -r requirements.txt
```

Or only the documentation dependencies:

```bash
pip install sphinx sphinx-rtd-theme sphinx-autobuild
```

## 2. Build HTML

```bash
sphinx-build -b html docs docs/_build/html
```

## 3. Open

Windows:

```powershell
start docs\_build\html\index.html
```

Linux:

```bash
xdg-open docs/_build/html/index.html
```

macOS:

```bash
open docs/_build/html/index.html
```

## 4. Live reload

```bash
sphinx-autobuild docs docs/_build/html
```

## 5. Clean rebuild

If you change configuration or get stale output:

```bash
sphinx-build -M clean docs docs/_build
sphinx-build -b html docs docs/_build/html
```

## What is documented?

- Project architecture
- Installation and execution
- Local pandas pipeline
- Reusable PySpark pipeline
- AWS Glue job
- S3/Glue/Athena architecture
- FastAPI endpoints
- Streamlit dashboard
- Terraform source
- SQL queries
- Python API reference generated with `autodoc`
- Source-code listings generated with `literalinclude`
