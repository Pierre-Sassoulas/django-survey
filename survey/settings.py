# -*- coding: utf-8 -*-

import os

from django.conf import settings

# Number of messages to display per page.
MESSAGES_PER_PAGE = getattr(settings, "ROSETTA_MESSAGES_PER_PAGE", 10)


ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(ROOT, "csv")

USER_DID_NOT_ANSWER = getattr(settings, "USER_DID_NOT_ANSWER", "Left blank")

TEX_CONFIGURATION_FILE = getattr(
    settings, "TEX_CONFIGURATION_FILE", os.path.join(ROOT, "doc", "example_conf.yaml")
)
SURVEY_DEFAULT_PIE_COLOR = getattr(settings, "SURVEY_DEFAULT_PIE_COLOR", "red!50")

CHOICES_SEPARATOR = getattr(settings, "CHOICES_SEPARATOR", ",")

MEDIA_URL = "/media/"
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(ROOT, "media")
STATIC_ROOT = os.path.join(ROOT, "static")

DEBUG_ADMIN_NAME = "test_admin"
DEBUG_ADMIN_PASSWORD = "test_password"

STATICFILES_DIRS = [os.path.normpath(os.path.join(ROOT, "..", "survey", "static"))]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(ROOT, "survey", "templates"),
            os.path.join(ROOT, "dev", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Default
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


INSTALLED_APPS = ("survey", "bootstrapform")

LOCALE_PATHS = (os.path.join(ROOT, "survey", "locale"),)
LANGUAGE_CODE = "en"
LANGUAGES = (
    ("en", "english"),
    ("ru-RU", "русский"),
    ("es", "spanish"),
    ("fr", "french"),
    ("ja", "Japanese"),
)
