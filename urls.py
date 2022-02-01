# pylint: disable=invalid-name

from django.conf.urls import include

try:
    from django.conf.urls import url
except ImportError:
    # Django 4.0 replaced url by something else
    # See https://stackoverflow.com/a/70319607/2519059
    from django.urls import re_path as url
from django.contrib import admin
from django.shortcuts import redirect
from django.urls.base import reverse


def home(request):
    """Permit to not get 404 while testing."""
    return redirect(reverse("survey-list"))


urlpatterns = [
    url(r"^$", home, name="home"),
    url("accounts/", include("django.contrib.auth.urls")),
    url(r"^rosetta/", include("rosetta.urls")),
    url(r"^survey/", include("survey.urls")),
    url(r"^admin/", admin.site.urls),
]
