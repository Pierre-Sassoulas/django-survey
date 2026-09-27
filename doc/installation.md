# Installation

Add `django-survey-and-report` to your requirements and get it with pip.

```bash
echo 'django-survey-and-report' >> requirements.txt
pip install -r requirements.txt
```

Add `survey` in the `INSTALLED_APPS` in your settings :

```python
INSTALLED_APPS = [
    # Your own installed apps here
]

from pathlib import Path

CSV_DIRECTORY = Path("csv")  # Define the directory where csv are exported
TEX_DIRECTORY = Path("tex")  # Define the directory where tex files and pdf are exported

INSTALLED_APPS += ["survey"]
```

Add a URL entry to your project’s urls.py, for example:

```python
from django.conf import settings
from django.urls import include, path

urlpatterns = [
    # Your own url pattern here
]

if "survey" in settings.INSTALLED_APPS:
    urlpatterns += [path("survey/", include("survey.urls"))]
```

Note: you can use whatever you wish as the URL prefix.

You can also change some options:

```python
# Permit to open the csv in Excel without problem with separator
# Using this trick : https://superuser.com/a/686415/567417
EXCEL_COMPATIBLE_CSV = True

# The separator for questions (Default to ",")
CHOICES_SEPARATOR = "|"

# What is shown in export when the user do not answer (Default to "Left blank")
USER_DID_NOT_ANSWER = "NAA"

# Path to the Tex configuration file (default to an internal file that should be sufficient)
from pathlib import Path

TEX_CONFIGURATION_FILE = Path("tex", "tex.conf")

# Default color for exported pdf pie (default to "red!50")
SURVEY_DEFAULT_PIE_COLOR = "blue!50"
```

To uninstall `django-survey-and-report`, simply comment out or remove the 'survey' line
in your `INSTALLED_APPS`.

If you want to use the pdf rendering you need to install `xelatex`. If you're using the
Sankey's diagram generation you will also have to install `python3-tk`.
