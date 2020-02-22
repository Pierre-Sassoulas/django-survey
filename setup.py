import sys
from os import path

import setuptools

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")

DESCRIPTION = (
    "A django survey app, based on and compatible with "
    '"django-survey". You will be able to migrate your data from an ancient '
    "version of django-survey, but it has been ported to python 3 and you can "
    "export results as CSV or PDF using your native language."
)

THIS_DIRECTORY = path.abspath(path.dirname(__file__))
with open(path.join(THIS_DIRECTORY, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


setuptools.setup(
    name="django-survey-and-report",
    version="1.3.18",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Pierre SASSOULAS",
    author_email="pierre.sassoulas@gmail.com",
    license="AGPL",
    url="https://github.com/Pierre-Sassoulas/django-survey",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Natural Language :: French",
        "Natural Language :: Japanese",
        "Natural Language :: Chinese (Traditional)",
        "Natural Language :: Russian",
        "Natural Language :: Spanish",
        "Natural Language :: German",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: Django",
    ],
    install_requires=[
        "django>=2.1.6",
        "django-bootstrap-form>=3.4",
        "django-tastypie>=0.14.2",  # API
        "django-registration>=3.0",  # account logic, views and workflows
        "pytz>=2018.9",
        "ordereddict>=1.1",
        "pyyaml>=4.2b1",
        "pySankeyBeta~=1.2.2",
    ],
    extras_require={
        "dev": [
            "django-rosetta",
            "coverage",
            "python-coveralls",
            "coveralls",
            "colorama",
            "pylint",
            "flake8",
            "pre-commit",
        ]
    },
)
