from survey.tests import BaseTest
from django.test import override_settings
from django.conf import settings
from django.test import tag
from survey import set_default_settings


@tag("set")
@override_settings()
class TestDefaultSettings(BaseTest):
    def test_set_choices_separator(self):
        url = "/admin/survey/survey/1/change/"
        del settings.CHOICES_SEPARATOR
        self.login()
        with self.assertRaises(AttributeError):
            self.client.get(url)
        set_default_settings()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
