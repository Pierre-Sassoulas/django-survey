import os

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = bool(os.environ.get("DEBUG", default=0))
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Add 'postgresql_psycopg2',
        # 'mysql', 'sqlite3' or 'oracle'
        "NAME": "survey.db",  # Or path to database file if using sqlite3
        "USER": "",  # Not used with sqlite3
        "PASSWORD": "",  # Not used with sqlite3.
        "HOST": "",  # Set to empty string for localhost. Not used with sqlite3
        "PORT": "",  # Set to empty string for default. Not used with sqlite3
    }
}
