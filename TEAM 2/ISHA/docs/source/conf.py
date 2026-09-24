import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "BMW Service Centre Capacity Intelligence"
author = "BMW Capstone Project"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
]

templates_path = ["_templates"]
exclude_patterns = []

language = "en"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_title = "BMW Service Centre Capacity Intelligence"
html_logo = None

master_doc = "index"

nitpicky = False

todo_include_todos = True
