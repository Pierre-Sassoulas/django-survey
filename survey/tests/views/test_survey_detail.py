# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.urls.base import reverse

from survey.tests import BaseTest
from survey.models import Response, Answer

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
        response = self.client.get(reverse("survey-detail", args=(4,)))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("survey-detail", args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_survey_non_editable(self):
        """
        Checks that a survey indicated as non editable cannot be edited by
        an authenticated user.
        """
        self.login()
        response = self.client.post(
            reverse("survey-detail", args=(1,)),
            data={
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
            reverse("survey-confirmation", args=(response_saved[0].interview_uuid,)),
        )

        response = self.client.post(
            reverse("survey-detail", args=(1,)),
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

    def test_multipage_survey(self):
        """
        Checks that multipage survey is working.
        """
        self.login()
        response = self.client.post(
            reverse("survey-detail", args=(5,)), data={"question_11": 42}
        )
        self.assertEqual(response.status_code, 302)

        response_saved = Response.objects.filter(
            user__username=settings.DEBUG_ADMIN_NAME, survey__id=5
        )
        self.assertEqual(len(response_saved.all()), 0)

        self.assertRedirects(response, reverse("survey-detail-step", args=(5, 1)))

        response = self.client.post(
            reverse("survey-detail-step", args=(5, 1)), data={"question_12": "yes"}
        )
        self.assertEqual(response.status_code, 302)

        response_saved = Response.objects.filter(
            user__username=settings.DEBUG_ADMIN_NAME, survey__id=5
        )
        self.assertEqual(len(response_saved.all()), 1)
        self.assertRedirects(
            response,
            reverse("survey-confirmation", args=(response_saved[0].interview_uuid,)),
        )

    def test_multipage_survey_edit(self):
        """
        Checks that a multipage survey can be rightfully edited.
        """
        self.login()
        # first creates the initial response
        response = self.client.post(
            reverse("survey-detail", args=(5,)), data={"question_11": 42}
        )
        response = self.client.post(
            reverse("survey-detail-step", args=(5, 1)), data={"question_12": "yes"}
        )
        response_saved = Response.objects.filter(
            user__username=settings.DEBUG_ADMIN_NAME, survey__id=5
        )
        self.assertEqual(len(response_saved.all()), 1)

        # tries normal edit
        response = self.client.post(
            reverse("survey-detail", args=(5,)), data={"question_11": 56}
        )
        response = self.client.post(
            reverse("survey-detail-step", args=(5, 1)), data={"question_12": "yes"}
        )
        response_saved = Response.objects.filter(
            user__username=settings.DEBUG_ADMIN_NAME, survey__id=5
        )
        self.assertEqual(len(response_saved.all()), 1)
        answer_saved = Answer.objects.filter(
            response__user__username=settings.DEBUG_ADMIN_NAME,
            response__survey__id=5,
            question__id=11,
        )
        self.assertEqual(len(answer_saved.all()), 1)
        self.assertEqual(answer_saved[0].body, "56")

        # tries forbidden edit (only a part of the form)
        response = self.client.post(
            reverse("survey-detail-step", args=(5, 1)), data={"question_12": "no"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("survey-list"))
        answer_saved = Answer.objects.filter(
            response__user__username=settings.DEBUG_ADMIN_NAME,
            response__survey__id=5,
            question__id=12,
        )
        self.assertEqual(len(answer_saved.all()), 1)
        self.assertEqual(answer_saved[0].body, "yes")
