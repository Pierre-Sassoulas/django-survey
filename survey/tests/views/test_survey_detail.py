import logging

from django.conf import settings
from django.urls.base import reverse

from survey.models import Answer, Response, Survey
from survey.tests import BaseTest

LOGGER = logging.getLogger(__name__)


class TestSurveyDetail(BaseTest):
    def test_survey_result(self):
        """We need logging for survey detail if the survey need login."""
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

        response_saved = Response.objects.filter(user__username=settings.DEBUG_ADMIN_NAME, survey__id=1)
        self.assertEqual(len(response_saved.all()), 1)
        self.assertEqual(response_saved[0].id, 15)

        self.assertRedirects(response, reverse("survey-confirmation", args=(response_saved[0].interview_uuid,)))

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
        response = self.client.post(reverse("survey-detail", args=(5,)), data={"question_11": 42})
        self.assertEqual(response.status_code, 302)

        response_saved = Response.objects.filter(user__username=settings.DEBUG_ADMIN_NAME, survey__id=5)
        self.assertEqual(len(response_saved.all()), 0)

        self.assertRedirects(response, reverse("survey-detail-step", args=(5, 1)))

        response = self.client.post(reverse("survey-detail-step", args=(5, 1)), data={"question_12": "yes"})
        self.assertEqual(response.status_code, 302)

        response_saved = Response.objects.filter(user__username=settings.DEBUG_ADMIN_NAME, survey__id=5)
        self.assertEqual(len(response_saved.all()), 1)
        self.assertRedirects(response, reverse("survey-confirmation", args=(response_saved[0].interview_uuid,)))

    def test_multipage_survey_edit(self):
        """
        Checks that a multipage survey can be rightfully edited.
        """
        self.login()
        # first creates the initial response
        response = self.client.post(reverse("survey-detail", args=(5,)), data={"question_11": 42})
        response = self.client.post(reverse("survey-detail-step", args=(5, 1)), data={"question_12": "yes"})
        response_saved = Response.objects.filter(user__username=settings.DEBUG_ADMIN_NAME, survey__id=5)
        self.assertEqual(len(response_saved.all()), 1)

        # tries normal edit
        response = self.client.post(reverse("survey-detail", args=(5,)), data={"question_11": 56})
        response = self.client.post(reverse("survey-detail-step", args=(5, 1)), data={"question_12": "yes"})
        response_saved = Response.objects.filter(user__username=settings.DEBUG_ADMIN_NAME, survey__id=5)
        self.assertEqual(len(response_saved.all()), 1)
        answer_saved = Answer.objects.filter(
            response__user__username=settings.DEBUG_ADMIN_NAME, response__survey__id=5, question__id=11
        )
        self.assertEqual(len(answer_saved.all()), 1)
        self.assertEqual(answer_saved[0].body, "56")

        # tries forbidden edit (only a part of the form)
        response = self.client.post(reverse("survey-detail-step", args=(5, 1)), data={"question_12": "no"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("survey-list"))
        answer_saved = Answer.objects.filter(
            response__user__username=settings.DEBUG_ADMIN_NAME, response__survey__id=5, question__id=12
        )
        self.assertEqual(len(answer_saved.all()), 1)
        self.assertEqual(answer_saved[0].body, "yes")

    def test_when_expiration_date_is_in_past_survey_is_not_visible(self):
        """when expiration_date is in the past the survey should be hidden"""
        response = self.client.get(reverse("survey-detail", args=(6,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("survey-list"))

    def test_when_publication_date_is_in_future_survey_is_not_visible(self):
        """when publish_date is in the future the survey should be hidden"""
        response = self.client.get(reverse("survey-detail", args=(7,)))
        self.assertEqual(response.status_code, 404)

    def test_when_expiration_date_is_in_past_survey_is_not_visible_via_post(self):
        """when expiration_date is in the past the survey should be hidden for post requests"""
        response = self.client.post(reverse("survey-detail", args=(6,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("survey-list"))

    def test_when_publication_date_is_in_future_survey_is_not_visible_via_post(self):
        """when publish_date is in the future the survey should be hidden for post requests"""
        response = self.client.post(reverse("survey-detail", args=(7,)))
        self.assertEqual(response.status_code, 404)

    def test_the_survey_should_be_visible(self):
        """when publish_date is in the past and expiration in the future
        the survey should be visible"""
        response = self.client.get(reverse("survey-detail", args=(8,)))
        self.assertEqual(response.status_code, 200)

    def test_the_survey_should_be_visible_while_no_expiration(self):
        """when publish_date is in the past and no expiration date is set
        the survey should be visible"""
        response = self.client.get(reverse("survey-detail", args=(9,)))
        self.assertEqual(response.status_code, 200)

    def test_the_survey_should_be_visible_while_no_publication_date(self):
        """when expiration_date is in the future and no publication_date is set
        the survey should be visible"""
        response = self.client.get(reverse("survey-detail", args=(10,)))
        self.assertEqual(response.status_code, 200)

    def test_when_the_survey_has_redirect_url(self):
        """when a survey has redirect url, should redirect to redirect_url"""
        response = self.client.post(
            reverse("survey-detail", args=(12,)),
            data={
                "question_16": "test answer",
            },
        )
        redirect_url = Survey.objects.get(pk=12).redirect_url
        self.assertRedirects(response, redirect_url, status_code=302, fetch_redirect_response=False)

    # def test_multipage_category_survey(self):
    #     """
    #     Checks that multipage survey is working.
    #     """
    #     self.login()
    #     response = self.client.post(reverse("survey-detail", args=(11,)), data={"question_13": 42, "question_15": 43})
    #     self.assertEqual(response.status_code, 302)
    #
    #     response_saved = Response.objects.filter(user__username=settings.DEBUG_ADMIN_NAME, survey__id=11)
    #     self.assertEqual(len(response_saved.all()), 0)
    #
    #     self.assertRedirects(response, reverse("survey-detail-step", args=(11, 1)))
    #
    #     response = self.client.post(reverse("survey-detail-step", args=(11, 1)), data={"question_14": "yes"})
    #     self.assertEqual(response.status_code, 302)
    #
    #     response_saved = Response.objects.filter(user__username=settings.DEBUG_ADMIN_NAME, survey__id=11)
    #     self.assertEqual(len(response_saved.all()), 1)
    #     self.assertRedirects(response, reverse("survey-confirmation", args=(response_saved[0].interview_uuid,)))
    #
    # def test_multipage_category_survey_edit(self):
    #     """
    #     Checks that a multipage category survey can be rightfully edited.
    #     """
    #     self.login()
    #     # first creates the initial response
    #     response = self.client.post(reverse("survey-detail", args=(11,)), data={"question_13": 42, "question_15": 43})
    #     response = self.client.post(reverse("survey-detail-step", args=(11, 1)), data={"question_14": "yes"})
    #     response_saved = Response.objects.filter(user__username=settings.DEBUG_ADMIN_NAME, survey__id=11)
    #     self.assertEqual(len(response_saved.all()), 1)
    #
    #     # tries normal edit
    #     response = self.client.post(reverse("survey-detail", args=(11,)), data={"question_13": 56, "question_15": 57})
    #     response = self.client.post(reverse("survey-detail-step", args=(11, 1)), data={"question_14": "yes"})
    #     response_saved = Response.objects.filter(user__username=settings.DEBUG_ADMIN_NAME, survey__id=11)
    #     self.assertEqual(len(response_saved.all()), 1)
    #     answer_saved = Answer.objects.filter(
    #         response__user__username=settings.DEBUG_ADMIN_NAME, response__survey__id=11, question__id=13
    #     )
    #     self.assertEqual(len(answer_saved.all()), 1)
    #     self.assertEqual(answer_saved[0].body, "56")
    #
    #     # tries forbidden edit (only a part of the form)
    #     response = self.client.post(reverse("survey-detail-step", args=(11, 1)), data={"question_14": "no"})
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse("survey-list"))
    #     answer_saved = Answer.objects.filter(
    #         response__user__username=settings.DEBUG_ADMIN_NAME, response__survey__id=11, question__id=14
    #     )
    #     self.assertEqual(len(answer_saved.all()), 1)
    #     self.assertEqual(answer_saved[0].body, "yes")
