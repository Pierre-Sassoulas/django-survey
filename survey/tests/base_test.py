from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

HERE = Path(__file__).parent


class BaseTest(TestCase):
    fixtures = [Path(HERE, "testdump.json")]

    def setUp(self):
        user = User(username=settings.DEBUG_ADMIN_NAME, is_superuser=True, is_staff=True)
        user.set_password(settings.DEBUG_ADMIN_PASSWORD)
        user.save()
        self.client = Client()

    def tearDown(self):
        self.logout()

    def login(self):
        """Log the user in."""
        is_logged = self.client.login(username=settings.DEBUG_ADMIN_NAME, password=settings.DEBUG_ADMIN_PASSWORD)
        if not is_logged:  # pragma: no cover
            raise ValueError("Login failed for test user! Tests won't work.")

    def logout(self):
        """Log the user out."""
        self.client.logout()
