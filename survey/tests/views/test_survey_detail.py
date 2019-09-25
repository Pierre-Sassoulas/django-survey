# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.urls.base import reverse

from survey.tests import BaseTest
from survey.models import Response

LOGGER = logging.getLogger(__name__)


class TestSurveyDetail(BaseTest):
    def test_survey_result(self):
        """ We need logging for survey detail if the survey need login. """
        response = self.client.get(reverse("survey-detail", args=(2,)))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("survey-detail", args=(1,)))
        self.assertEqual(response.status_code, 302)
        self.login()
        response = self.client.get(reverse("survey-detail", args=(2,)))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("survey-detail", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_survey_non_editable(self):
        self.login()
        response = self.client.post(
            reverse("survey-detail", args=[1]),
            data={
                "question_1": "no",
                "question_1": "maybe",
                "question_2": "no",
                "question_3": "This is a test of text",
                "question_4": "no",
                "question_5": 42,
                "question_6": "whatever",
            },
        )
        LOGGER.info(response.content)
        self.assertEqual(response.status_code, 302)

        response_saved = Response.objects.filter(
            user__username=settings.DEBUG_ADMIN_NAME, survey__id=1
        )
        self.assertEqual(len(response_saved.all()), 1)
        self.assertEqual(response_saved[0].id, 15)

        self.assertRedirects(
            response,
            reverse("survey-confirmation", args=[response_saved[0].interview_uuid]),
        )

        response = self.client.post(
            reverse("survey-detail", args=[1]),
            data={
                "question_1": "maybe",
                "question_2": "no",
                "question_3": "This is a test of edited text",
                "question_4": "maybe",
                "question_5": 4224,
                "question_6": "maybe",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("survey-list"))
