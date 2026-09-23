# Configuration file for the Sphinx documentation builder.

from pathlib import Path
import sys

# Make the repository root importable so autodoc can import the ``src`` package.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

project = "EV Range & Driving Efficiency Analytics"
author = "BMW Techworks India - Team 1"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",       # Generate API pages from Python docstrings.
    "sphinx.ext.napoleon",      # Support Google/NumPy-style docstrings.
    "sphinx.ext.viewcode",      # Add links to highlighted source code.
    "sphinx.ext.intersphinx",   # Link selected Python documentation externally.
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = []

# Mock AWS Glue imports because Glue-specific modules are unavailable on a
# normal local machine. The generated docs still show the Glue source via
# literalinclude, while local autodoc covers the reusable ``src`` package.
autodoc_mock_imports = [
    "awsglue",
    "boto3",
    "pyspark",
    "pandas",
    "fastapi",
    "streamlit",
    "dotenv",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
