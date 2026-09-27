"""Sphinx configuration for the django-survey-and-report documentation."""

from importlib import metadata

project = "django-survey-and-report"
author = "Pierre Sassoulas"
copyright = "%Y, Pierre Sassoulas"

try:
    release = metadata.version("django-survey-and-report")
except metadata.PackageNotFoundError:
    release = "unknown"

extensions = ["myst_parser"]
source_suffix = {".md": "markdown"}
exclude_patterns = ["_build"]

# Generate anchors for headings so that links like '#launching-tests' work
myst_heading_anchors = 4

html_theme = "furo"
html_title = "Django survey"
