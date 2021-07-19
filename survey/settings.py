import os
from pathlib import Path

from django.conf import settings

# Number of messages to display per page.
MESSAGES_PER_PAGE = getattr(settings, "ROSETTA_MESSAGES_PER_PAGE", 10)


ROOT = os.path.dirname(os.path.abspath(__file__))
USER_DID_NOT_ANSWER = getattr(settings, "USER_DID_NOT_ANSWER", "Left blank")
TEX_CONFIGURATION_FILE = getattr(settings, "TEX_CONFIGURATION_FILE", Path(ROOT, "doc", "example_conf.yaml"))
SURVEY_DEFAULT_PIE_COLOR = getattr(settings, "SURVEY_DEFAULT_PIE_COLOR", "red!50")
CHOICES_SEPARATOR = getattr(settings, "CHOICES_SEPARATOR", ",")
EXCEL_COMPATIBLE_CSV = False
DEFAULT_SURVEY_PUBLISHING_DURATION = 7

MEDIA_URL = "/media/"
STATIC_URL = "/static/"

MEDIA_ROOT = Path(ROOT, "media")
STATIC_ROOT = Path(ROOT, "static")

DEBUG_ADMIN_NAME = "test_admin"
DEBUG_ADMIN_PASSWORD = "test_password"

STATICFILES_DIRS = [os.path.normpath(Path(ROOT, "..", "survey", "static"))]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(ROOT, "survey", "templates"), Path(ROOT, "dev", "templates")],
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

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOCALE_PATHS = (Path(ROOT, "survey", "locale"),)
LANGUAGE_CODE = "en"
LANGUAGES = (
    ("en", "english"),
    ("ru", "russian"),
    ("es", "spanish"),
    ("fr", "french"),
    ("ja", "Japanese"),
    ("nl", "Dutch"),
    ("zh", "Chinese"),
    ("de", "German"),
    ("id", "Indonesian"),
    ("pt", "Portuguese"),
    ("pl", "Polish"),
)
