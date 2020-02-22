# -*- coding: utf-8 -*-

from pathlib import Path

from django.contrib.auth.models import User

from survey.models import Answer, Question, Response, Survey
from survey.tests import BaseTest

HERE = Path(__file__).parent


class TestManagement(BaseTest):

    """ Permit to check if export result is working as intended. """

    def create_answers(self, username, a1, a2, a3):
        if username:
            response = Response.objects.create(survey=self.survey, user=User.objects.create(username=username))
        else:
            response = Response.objects.create(survey=self.survey)
        response.save()
        Answer.objects.create(response=response, question=self.qst1, body=a1)
        Answer.objects.create(response=response, question=self.qst2, body=a2)
        Answer.objects.create(response=response, question=self.qst3, body=a3)

    def create_survey(self):
        self.test_managament_survey_name = "Test Management Survëy"
        self.survey = Survey.objects.create(
            name=self.test_managament_survey_name, is_published=True, need_logged_user=True, display_by_question=True
        )
        self.qst1 = Question.objects.create(text="Aèbc?", order=1, required=True, survey=self.survey)
        self.qst2 = Question.objects.create(text="Bècd?", order=2, required=False, survey=self.survey)
        self.qst3 = Question.objects.create(text="Cède?", order=3, required=True, survey=self.survey)
        self.qst4 = Question.objects.create(text="Dèef?", order=4, required=False, survey=self.survey)
        self.response = Response.objects.create(survey=self.survey, user=User.objects.all()[0])
        self.ans1 = Answer.objects.create(response=self.response, question=self.qst1, body="1é")
        self.ans2 = Answer.objects.create(response=self.response, question=self.qst2, body="2é")
        self.ans3 = Answer.objects.create(response=self.response, question=self.qst3, body="3é")
        self.response_null = Response.objects.create(survey=self.survey, user=User.objects.all()[1])
        self.empty = Answer.objects.create(response=self.response_null, question=self.qst3, body="")
        self.username = "SlctMltipl"
        self.create_answers(self.username, "[u'1', u'1a', u'1b']", "[u'2', u'2a', u'2b']", "[u'3', u'3a', u'3b']")
        self.other_username = "SlctSimilar"
        self.create_answers(
            self.other_username, "[u'1e', u'1é', u'1ë']", "[u'2e', u'2é', u'2ë']", "[u'3e', u'3é', u'3ë']"
        )
        self.create_answers(None, "", "", "")

    def create_big_ranking_survey(self, with_user=False):
        """ Load a big survey with Anonymous user rating question from 1 to
        5 à la Amazon review."""
        ranking_survey_name = "Big ranking survey"
        number_of_question = 10
        number_of_participant = 100
        ranking_survey = Survey.objects.create(
            name=ranking_survey_name, is_published=True, need_logged_user=False, display_by_question=True
        )
        questions = []
        question_choices = ["1,2,3,4,5"]
        if with_user:
            for j in range(number_of_participant):
                User.objects.get_or_create(username=j)
        for i in range(number_of_question):
            question = Question.objects.create(
                text="How much do you like question {} ?".format(i + 1),
                order=i,
                required=True,
                survey=ranking_survey,
                choices=question_choices,
            )
            questions.append(question)
        for j in range(number_of_participant):
            user = None
            if with_user:
                user = User.objects.get(username=j)
            response = Response.objects.create(survey=ranking_survey, user=user)
            for i, question in enumerate(questions):
                answer = j % (i + 1) % 5 + 1
                Answer.objects.create(response=response, question=question, body=answer)

    def setUp(self):
        BaseTest.setUp(self)
        self.create_survey()
        self.expected_content = """\
user,Aèbc?,Bècd?,Cède?,Dèef?
ps250112,1é,2é,3é,
pierre,,,,
{},1|1a|1b,2|2a|2b,3|3a|3b,
{},1e|1é|1ë,2e|2é|2ë,3e|3é|3ë,
Anonymous,,,,""".format(
            self.username, self.other_username
        )
        self.expected_header = ["user", "Aèbc?", "Bècd?", "Cède?", "Dèef?"]
        self.conf_dir = Path(HERE, "..", "exporter", "tex")
        self.test_conf_path = Path(self.conf_dir, "test_conf.yaml")
