# Django survey

A django survey app, based on and compatible with "django-survey". You will be able to
migrate your data from an ancient version of django-survey, but it has been ported to
python 3 and you can export results as CSV or PDF using your native language.

If you want the latest version still compatible with python 2.7 you need a version <
1.3.0.

Professional support for django-survey-and-report is available as part of the
[Tidelift Subscription](https://tidelift.com/subscription/pkg/pypi-django-survey-and-report?utm_source=pypi-django-survey-and-report&utm_medium=referral&utm_campaign=enterprise)

[![Build Status](https://travis-ci.org/Pierre-Sassoulas/django-survey.svg?branch=master)](https://travis-ci.org/Pierre-Sassoulas/django-survey)
[![Coverage Status](https://coveralls.io/repos/github/Pierre-Sassoulas/django-survey/badge.svg?branch=master)](https://coveralls.io/github/Pierre-Sassoulas/django-survey?branch=master)
[![PyPI version](https://badge.fury.io/py/django-survey-and-report.svg)](https://badge.fury.io/py/django-survey-and-report)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

## Table of contents

- [Contributing as a developer](#contributing-as-a-developer)
  - [Development environment](#development-environment)
  - [Committing code](#committing-code)
    - [Launching tests](#launching-tests)
    - [Adding test data](#adding-test-data)
    - [Launching coverage](#launching-coverage)
    - [Applying Lint](#applying-lint)
- [Translating the project](#translating-the-project)
  - [As a developer](#as-a-developer)
  - [As a translator](#as-a-translator)

## Contributing as a developer

### Development environment

This is the typical command you should do to get started:

```bash
python -m venv venv/ # Create virtualenv
source venv/bin/activate # Activate virtualenv
pip install -e ".[dev]" # Install dev requirements
pre-commit install # Install pre-commit hook framework
python manage.py migrate # Create database
python manage.py loaddata survey/tests/testdump.json # Load test data
python manage.py createsuperuser
python manage.py runserver # Launch server
```

Please note that `pre-commit` will permit to fix a lot of linting error automatically
and is not required but highly recommended.

### Committing code

#### Launching tests

```bash
python manage.py test survey
```

#### Adding test data

If you want to dump a test database after adding data to it, this is the command to have
a minimal diff :

```bash
python manage.py dumpdata --format json -e contenttypes -e admin -e auth.Permission
-e sessions.session -e sites.site --natural-foreign --indent 1
-o survey/tests/testdump.json
```

#### Launching coverage

```bash
coverage run --source=survey --omit=survey/migrations/* ./manage.py test
coverage html
xdg-open htmlcov/index.html
```

#### Applying Lint

We're using `pre-commit`, it should take care of linting during commit.

## Translating the project

Django survey's is available in multiple language. Your contribution would be very
appreciated if you know a language that is not yet available.

### As a developer

If your language does not exist add it in the `LANGUAGE` variable in the settings, like
[here](https://github.com/Pierre-Sassoulas/django-survey/commit/ee3bdba26c303ad12fc4584938e724b39223faa9#diff-bdf3ecebd8379ca98cc89e545fc90899).
Do not forget to credit yourself like in the header seen
[here](https://github.com/Pierre-Sassoulas/django-zxcvbn-password-validator/commit/274d7c9b27268a0455f80ea518c452532b970ea4#diff-8015f170326f20998060314fda9b92b1)

Then you can translate with :

```bash
python manage.py makemessages
# python manage.py createsuperuser ? (You need to login for rosetta)
python manage.py runserver
# Access http://localhost:8000/admin to login
# Then go to http://localhost:8000/rosetta to translate
python manage.py makemessages --no-obsolete --no-wrap --ignore venv --locale de \
  --locale es --locale fr  --locale id --locale ja --locale nl --locale pl \
  --locale pt --locale ru --locale tr --locale zh
git add survey/locale/
...
```

If your language is not yet available in rosetta,
[this stack overflow question](https://stackoverflow.com/questions/12946830/) should
work even for language not handled by django.

### As a translator

If you're not a developer, open an issue on github and ask for a .po file in your
language. I will generate it for you, so you can edit it with an online editor. I will
then create the .po and commit them, so you can edit them with your github account or
integrate it myself if you do not have one. You will be credited
[here](https://github.com/Pierre-Sassoulas/django-survey#language-available).
