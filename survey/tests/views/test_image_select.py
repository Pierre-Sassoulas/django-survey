from django.urls.base import reverse

from survey.models import Answer, Question, Survey
from survey.tests import BaseTest


class TestImageSelect(BaseTest):
    def setUp(self):
        super().setUp()
        self.survey = Survey.objects.create(
            name="Favorite pet",
            is_published=True,
            need_logged_user=False,
            display_method=Survey.ALL_IN_ONE_PAGE,
        )
        self.question = Question.objects.create(
            text="Which pet do you like?",
            choices="cat:/static/cat.png, dog:/static/dog.png",
            order=1,
            required=True,
            survey=self.survey,
            type=Question.SELECT_IMAGE,
        )
        self.url = reverse("survey-detail", args=(self.survey.id,))

    def test_render(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'src="/static/cat.png"')
        self.assertContains(response, 'src="/static/dog.png"')
        self.assertContains(response, "survey/js/survey.js")

    def test_submit(self):
        choice_value, _ = self.question.get_choices()[1]
        response = self.client.post(self.url, data={f"question_{self.question.id}": choice_value})
        self.assertEqual(response.status_code, 302)
        answer = Answer.objects.get(question=self.question)
        self.assertEqual(answer.body, choice_value)
