[![Build Status](https://github.com/Pierre-Sassoulas/django-survey/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Pierre-Sassoulas/django-survey/actions)
[![Coverage Status](https://coveralls.io/repos/github/Pierre-Sassoulas/django-survey/badge.svg?branch=main)](https://coveralls.io/github/Pierre-Sassoulas/django-survey?branch=main)
[![Documentation Status](https://readthedocs.org/projects/django-survey-and-report/badge/?version=latest)](https://django-survey-and-report.readthedocs.io/)
[![PyPI version](https://badge.fury.io/py/django-survey-and-report.svg)](https://badge.fury.io/py/django-survey-and-report)
[![Published on Django Packages](https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26)](https://djangopackages.org/packages/p/django-survey-and-report/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

# Django survey

A django survey app that can export results as CSV or PDF using your native language.

`django-survey-and-report` on pypi. Based on and compatible with `django-survey`. You
will be able to migrate your data from an ancient version of `django-survey`, but it has
been ported to python 3, and you can export results as CSV or PDF using your native
language.

Professional support for django-survey-and-report is available as part of the
[Tidelift Subscription](https://tidelift.com/subscription/pkg/pypi-django-survey-and-report?utm_source=pypi-django-survey-and-report&utm_medium=referral&utm_campaign=enterprise)

The documentation is available at https://django-survey-and-report.readthedocs.io/.

## Quick start

Install the package:

```bash
pip install django-survey-and-report
```

Add `survey` in the `INSTALLED_APPS` in your settings:

```python
INSTALLED_APPS += ["survey"]
```

Add a URL entry to your project's `urls.py`:

```python
from django.urls import include, path

urlpatterns += [path("survey/", include("survey.urls"))]
```

Then create your first survey in the admin. See the
[installation guide](https://django-survey-and-report.readthedocs.io/en/latest/installation.html)
for all the settings, and how to generate CSV and PDF reports.

## Contributing

See
[CONTRIBUTING.md](https://github.com/Pierre-Sassoulas/django-survey/blob/main/CONTRIBUTING.md).
