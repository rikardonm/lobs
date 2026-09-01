# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# Add src to path so we can import lobs
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# -- Project information -----------------------------------------------------

project = 'lobs'
copyright = '2025, ricardo'
author = 'ricardo'
release = os.environ.get('VERSION', '0.0.1')

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx_design',
    'myst_parser',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'

# RTD theme configuration
html_theme_options = {
    'display_version': True,
    'style_nav_header_background': '#2c3e50',
    'collapse_navigation': False,
    'navigation_depth': 4,
}

html_static_path = ['_static']

# Custom theme settings
html_title = 'lobs Documentation'
html_short_title = 'lobs'

# Add custom CSS
html_css_files = [
    'custom.css',
]

html_context = {
    'default_mode': 'auto',
}

# -- Options for HTML help output --------------------------------------------

htmlhelp_basename = 'lobsdoc'

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    'papersize': 'letterpaper',
    'preamble': r'''
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}  # clear all header and footer fields
\rhead{\thepage}
\lhead{\leftmark}
''',
}

latex_documents = [
    ('index', 'lobs.tex', 'lobs Documentation',
     'ricardo', 'manual'),
]

# -- MyST Parser configuration -----------------------------------------------

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# -- Autodoc configuration ---------------------------------------------------

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'member-order': 'bysource',
}

autodoc_typehints = 'description'
