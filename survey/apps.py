from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoSurveyAndReportConfig(AppConfig):
    """
    See https://docs.djangoproject.com/en/2.1/ref/applications/#django.apps.AppConfig
    """

    name = "survey"
    label = "survey"
    verbose_name = _("Survey and report")
