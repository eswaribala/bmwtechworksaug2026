project = 'BMW Snowflake Incremental Data Warehouse'
copyright = '2026, BMW Data Platform Capstone'
author = 'Project Documentation'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
html_title = 'BMW Snowflake Incremental Data Warehouse'
html_static_path = ['_static']
html_css_files = ['custom.css']

master_doc = 'index'

graphviz_output_format = 'svg'

rst_prolog = r'''
.. role:: sql(code)
   :language: sql

.. role:: powershell(code)
   :language: powershell
'''
