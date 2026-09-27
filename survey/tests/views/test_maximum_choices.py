from django.urls.base import reverse

from survey.models import Question, Response
from survey.tests import BaseTest


class TestMaximumChoices(BaseTest):
    def setUp(self):
        super().setUp()
        self.question = Question.objects.get(pk=7)
        self.question.maximum_choices = 2
        self.question.save()
        self.url = reverse("survey-detail", args=(2,))
        self.response_count = Response.objects.filter(survey__id=2).count()

    def test_too_many_choices_is_refused(self):
        response = self.client.post(self.url, data={"question_7": ["1", "2", "3"]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select at most 2 choices.")
        self.assertEqual(Response.objects.filter(survey__id=2).count(), self.response_count)

    def test_maximum_choices_is_accepted(self):
        response = self.client.post(self.url, data={"question_7": ["1", "2"]})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Response.objects.filter(survey__id=2).count(), self.response_count + 1)

    def test_no_limit_without_maximum_choices(self):
        self.question.maximum_choices = None
        self.question.save()
        response = self.client.post(self.url, data={"question_7": ["1", "2", "3", "4", "5"]})
        self.assertEqual(response.status_code, 302)
