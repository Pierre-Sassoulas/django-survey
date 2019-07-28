from survey.tests import BaseTest
from django.test import override_settings
from django.conf import settings
from survey import set_default_settings
from survey.exporter.tex.survey2tex import Survey2Tex


@override_settings()
class TestDefaultSettings(BaseTest):
    def test_set_choices_separator(self):
        url = "/admin/survey/survey/1/change/"
        del settings.CHOICES_SEPARATOR
        self.login()
        set_default_settings()
        try:
            self.client.get(url)
        except AttributeError:
            self.fail("AttributeError: survey failed to set CHOICES_SEPARATOR")

    def test_set_root(self):
        del settings.ROOT
        set_default_settings()
        try:
            getattr(settings, "ROOT")
        except AttributeError:
            self.fail("AttributeError: survey failed to set ROOT")
