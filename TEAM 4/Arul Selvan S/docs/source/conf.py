project = "BMW Natural Language Analyst"
copyright = "2026, BMW Natural Language Analyst"
author = "BMW Natural Language Analyst"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"

import os
import sys
sys.path.insert(0, os.path.abspath("../../src"))
