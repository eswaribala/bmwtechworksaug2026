"""Sphinx configuration for the BMW Dealer Scoreboard documentation."""

from datetime import date
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

project = "BMW Dealer Scoreboard Performance"
copyright = f"2026, BMW Techworks India Private Limited"
author = "BMW Techworks India Private Limited"
release = "1.0"
today = date.today().isoformat()

extensions = ["sphinx.ext.todo"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_title = "BMW Dealer Scoreboard Performance"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
todo_include_todos = True

rst_prolog = """
.. role:: aws(code)
   :language: text
"""