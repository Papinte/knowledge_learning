# docs/conf.py

# Configuration file for the Sphinx documentation builder.

# Add the project root to the Python path
import os
import sys

sys.path.insert(0, r"C:\Users\Antoi\Desktop\knowledge_learning")

# Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'knowledge.settings'

# Setup Django
import django
django.setup()

# Project information
project = 'Knowledge Learning'
copyright = '2025, Antoine Papin'
author = 'Antoine Papin'
release = '1.0'

# Add extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

# Theme
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']