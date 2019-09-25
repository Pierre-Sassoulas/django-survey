# -*- coding: utf-8 -*-

from django.conf import settings
from django.urls.base import reverse

from survey.tests import BaseTest


class TestSurveyAuthRequired(BaseTest):

    """ Permit to check if need_logged_user is working as intended. """

    def assert_accessible(self, url):
        """ Assert that everything is accessible. """
        try:
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.login()
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.logout()
        except Exception as exc:  # pragma: no cover
            exc.args += ((url),)
            raise

    def test_need_login(self):
        """ If a survey has need_logged_user=True user need to authenticate."""
        urls = [
            reverse("survey-detail", kwargs={"id": 1}),
            reverse("survey-completed", kwargs={"id": 1}),
            reverse("survey-detail-step", kwargs={"id": 1, "step": 1}),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(settings.LOGIN_URL in response["location"])
            self.login()
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.logout()

    def test_accessible(self):
        """ If need_logged_user=False user do not need to authenticate. """
        urls = [
            reverse("survey-list"),
            reverse("survey-detail", kwargs={"id": 2}),
            reverse("survey-completed", kwargs={"id": 2}),
            reverse("survey-detail-step", kwargs={"id": 2, "step": 1}),
            reverse("survey-confirmation", kwargs={"uuid": "fake"}),
        ]
        for url in urls:
            self.assert_accessible(url)
