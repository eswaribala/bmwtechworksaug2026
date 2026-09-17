"""Sphinx configuration for the BMW Data Quality & Governance Platform."""

from __future__ import annotations

import os
import sys

# Make the project root importable so autodoc can find `src` and `backend`.
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
project = "BMW Data Quality & Governance Platform"
copyright = "2026, Participant 12 | Pod D"
author = "Participant 12 | Pod D"
release = "1.0.0"

# -- General configuration ----------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Autodoc / autosummary -----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_typehints = "description"
autosummary_generate = True

napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- HTML output ---------------------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
