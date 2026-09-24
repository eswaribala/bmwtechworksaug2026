from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

project = "EV Battery Health Intelligence"
author = "Capstone Project Team"
release = "0.1.0"
copyright = "2026, Capstone Project Team"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.mermaid",
]

autodoc_mock_imports = [
    "boto3",
    "botocore",
    "pyspark",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"
html_static_path = []

nitpicky = False
highlight_language = "python"
