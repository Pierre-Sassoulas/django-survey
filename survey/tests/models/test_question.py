# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils.translation import gettext_lazy as _

from survey.models import Answer, Question, Response, Survey
from survey.tests.models import BaseModelTest

try:
    from _collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class TestQuestion(BaseModelTest):
    def setUp(self):
        BaseModelTest.setUp(self)
        text = "Lorem ipsum dolor sit amët, <strong> consectetur </strong> adipiscing elit."
        self.question = Question.objects.get(text=text)
        choices = "abé cé, Abë-cè, Abé Cé, dé, Dé, dë"
        self.questions[0].choices = choices
        self.questions[2].choices = choices
        self.survey = Survey.objects.create(
            name="Test", is_published=True, need_logged_user=False, display_method=Survey.ALL_IN_ONE_PAGE
        )
        user_number = len(self.questions[0].choices.split(", "))
        for i in range(user_number):
            user = User.objects.create(username="User {}".format(i))
            Response.objects.create(survey=self.survey, user=user)
        for i, choice in enumerate(self.questions[0].choices.split(", ")):
            user = User.objects.get(username="User {}".format(i))
            response = Response.objects.get(user=user, survey=self.survey)
            Answer.objects.create(question=self.questions[0], body=choice, response=response)
            q2_choice = "dë" if "b" in choice else "Abë-cè"
            Answer.objects.create(question=self.questions[2], body=q2_choice, response=response)
        # Shortcut for the first question's answer cardinality's function
        self.card = self.questions[0].answers_cardinality
        self.sorted_card = self.questions[0].sorted_answers_cardinality

    def test_unicode(self):
        """ Unicode generation. """
        self.assertIsNotNone(str(self.questions[0]))

    def test_get_choices(self):
        """ We can get a list of choices for a widget from choices text. """
        self.questions[0].choices = "A éa,B éb"
        self.assertEqual(self.questions[0].get_choices(), (("a-éa", "A éa"), ("b-éb", "B éb")))
        self.questions[0].choices = "A()a,  ,C()c"
        self.assertEqual(self.questions[0].get_choices(), (("aa", "A()a"), ("cc", "C()c")))
        self.questions[0].choices = "Женщина,Мужчина"
        self.assertEqual(self.questions[0].get_choices(), (("женщина", "Женщина"), ("мужчина", "Мужчина")))
        self.questions[0].choices = "聖黎,はじむ"
        self.assertEqual(self.questions[0].get_choices(), (("聖黎", "聖黎"), ("はじむ", "はじむ")))

    @override_settings(CHOICES_SEPARATOR="|")
    def test_get_choices_with_pipe(self):
        """ We can get a list of choices for a widget from choices text with_pipe. """
        self.questions[0].choices = "A éa|B éb"
        self.assertEqual(self.questions[0].get_choices(), (("a-éa", "A éa"), ("b-éb", "B éb")))
        self.questions[0].choices = "A()a|  |C()c"
        self.assertEqual(self.questions[0].get_choices(), (("aa", "A()a"), ("cc", "C()c")))
        self.questions[0].choices = "Yes, I do| No, I don't"
        self.assertEqual(self.questions[0].get_choices(), (("yes-i-do", "Yes, I do"), ("no-i-dont", "No, I don't")))
        self.questions[0].choices = "Женщина|Мужчина"
        self.assertEqual(self.questions[0].get_choices(), (("женщина", "Женщина"), ("мужчина", "Мужчина")))
        self.questions[0].choices = "聖黎|はじむ"
        self.assertEqual(self.questions[0].get_choices(), (("聖黎", "聖黎"), ("はじむ", "はじむ")))

    def test_validate_choices(self):
        """  List are validated for comma. """
        question = Question.objects.create(
            text="Q?", choices="a,b,c", order=1, required=True, survey=self.survey, type=Question.SELECT_MULTIPLE
        )
        question.choices = "a"
        self.assertRaises(ValidationError, question.save)
        question.choices = ",a"
        self.assertRaises(ValidationError, question.save)
        question.choices = "a,"
        self.assertRaises(ValidationError, question.save)
        question.choices = ",a,  ,"
        self.assertRaises(ValidationError, question.save)

    @override_settings(CHOICES_SEPARATOR="|")
    def test_validate_choices_with_pipe(self):
        """  List are validated for pipe. """
        question = Question.objects.create(
            text="Q?", choices="a|b|c", order=1, required=True, survey=self.survey, type=Question.SELECT_MULTIPLE
        )
        question.choices = "a"
        self.assertRaises(ValidationError, question.save)
        question.choices = "|a"
        self.assertRaises(ValidationError, question.save)
        question.choices = "a,"
        self.assertRaises(ValidationError, question.save)
        question.choices = "|a|  |"
        self.assertRaises(ValidationError, question.save)

    def test_answers_as_text(self):
        """ We can get a list of answers to this question. """
        qat = self.question.answers_as_text
        self.assertEqual(3, len(qat))
        expected = ["Yës", "Maybe", "Yës"]
        expected.sort()
        qat.sort()
        self.assertEqual(qat, expected)

    def test_answer_cardinality_type(self):
        """ We always return an OrderedDict. """
        self.assertIsInstance(self.card(), OrderedDict)
        self.assertIsInstance(self.sorted_card(), OrderedDict)

    def test_answers_cardinality(self):
        """ We can get the cardinality of each answers. """
        self.assertEqual(self.question.answers_cardinality(), {"Maybe": 1, "Yës": 2})
        self.assertEqual(self.question.answers_cardinality(min_cardinality=2), {"Other": 1, "Yës": 2})
        question = Question.objects.get(text="Ipsum dolor sit amët, <strong> consectetur </strong>  adipiscing elit.")
        self.assertEqual({"No": 1, "Yës": 1}, question.answers_cardinality())
        question = Question.objects.get(text="Dolor sit amët, <strong> consectetur</strong>  adipiscing elit.")
        self.assertEqual({"": 1, "Text for a response": 1}, question.answers_cardinality())
        question = Question.objects.get(text="Ipsum dolor sit amët, consectetur <strong> adipiscing </strong> elit.")
        self.assertEqual({"1": 1, "2": 1}, question.answers_cardinality())
        question = Question.objects.get(text="Dolor sit amët, consectetur<strong>  adipiscing</strong>  elit.")
        self.assertEqual({"No": 1, "Whatever": 1, "Yës": 1}, question.answers_cardinality())
        self.assertEqual({"Näh": 2, "Yës": 1}, question.answers_cardinality(group_together={"Näh": ["No", "Whatever"]}))

    def test_answers_cardinality_grouped(self):
        """ We can group answers taking letter case or slug into account. """
        self.assertEqual(self.card(), {"abé cé": 1, "Abé Cé": 1, "Abë-cè": 1, "dé": 1, "dë": 1, "Dé": 1})
        self.assertEqual(
            self.card(group_together={"ABC": ["abé cé", "Abë-cè", "Abé Cé"], "D": ["dé", "Dé", "dë"]}),
            {"ABC": 3, "D": 3},
        )
        self.assertEqual(self.card(group_by_letter_case=True), {"abé cé": 2, "abë-cè": 1, "dé": 2, "dë": 1})
        self.assertEqual(self.card(group_by_slugify=True), {"abe-ce": 3, "de": 3})
        self.assertEqual(self.card(group_by_slugify=True, group_together={"ABCD": ["abe-ce", "de"]}), {"ABCD": 6})
        self.assertEqual(
            self.card(group_by_letter_case=True, group_together={"ABCD": ["Abë-cè", "Abé Cé", "Dé", "dë"]}), {"ABCD": 6}
        )

    def test_answers_cardinality_filtered(self):
        """ We can filter answer with a csv string. """
        self.assertEqual(self.card(filter=["abé cé", "Abë-cè"], group_by_slugify=True), {"de": 3})
        self.assertEqual(self.card(filter=["abe-ce"], group_by_slugify=True), {"de": 3})
        self.assertEqual(
            self.card(group_together={"ABC": ["abe-ce"]}, filter=["ABC"], group_by_slugify=True), {"de": 3}
        )
        self.assertEqual(self.card(filter=["abé cé", "Abë-cè"], group_by_letter_case=True), {"dé": 2, "dë": 1})
        self.assertEqual(self.card(filter=["abé cé", "Abë-cè"]), {"Abé Cé": 1, "dé": 1, "dë": 1, "Dé": 1})

    def test_answers_cardinality_linked(self):
        """ We can get the answer to another question instead"""
        abc_together = {"ABC": ["abé cé", "Abë-cè", "Abé Cé"]}
        abcd_together = {"ABC": ["abé cé", "Abë-cè", "Abé Cé"], "D": ["dé", "Dé", "dë"]}
        self.assertRaises(TypeError, self.card, other_question="str")
        self.assertEqual(
            self.card(other_question=self.questions[2]),
            {
                "abé cé": {"dë": 1},
                "Abë-cè": {"dë": 1},
                "Abé Cé": {"dë": 1},
                "dé": {"Abë-cè": 1},
                "Dé": {"Abë-cè": 1},
                "dë": {"Abë-cè": 1},
            },
        )
        self.assertEqual(
            self.card(other_question=self.questions[2], group_together=abcd_together),
            {"ABC": {"D": 3}, "D": {"ABC": 3}},
        )
        self.assertEqual(
            self.card(other_question=self.questions[2], filter=["dé"], group_together=abc_together),
            {"ABC": {"dë": 3}, "Dé": {"ABC": 1}, "dë": {"ABC": 1}},
        )
        self.assertEqual(
            self.card(other_question=self.questions[2], filter=["dë"], group_together=abc_together),
            {"Dé": {"ABC": 1}, "dé": {"ABC": 1}},
        )
        for i in [0, 2]:
            user = User.objects.get(username="User {}".format(i))
            response = Response.objects.get(survey=self.survey, user=user)
            answer = Answer.objects.get(question=self.questions[2], response=response)
            answer.delete()
        self.assertEqual(
            self.card(other_question=self.questions[2], group_together=abcd_together),
            {"ABC": {"D": 1, _(settings.USER_DID_NOT_ANSWER): 2}, "D": {"ABC": 3}},
        )

    def test_answers_cardinality_linked_without_link(self):
        """ When we want to link to another question and there is no link at
        all, we still have a dict. """
        survey = Survey.objects.create(
            name="name", is_published=True, need_logged_user=False, display_method=Survey.BY_QUESTION
        )
        questions = []
        question_choices = "1,2,3"
        for i in range(3):
            question = Question.objects.create(
                text=str(i + 1), order=i, required=True, survey=survey, choices=question_choices
            )
            questions.append(question)
        for j in range(3):
            response = Response.objects.create(survey=survey)
            for i, question in enumerate(questions):
                Answer.objects.create(response=response, question=question, body=(j + i))
        expected = [
            ("Left blank", {"1": 1, "2": 1, "3": 1}),
            ("0", {"Left blank": 1}),
            ("1", {"Left blank": 1}),
            ("2", {"Left blank": 1}),
        ]
        self.assertEqual(questions[0].sorted_answers_cardinality(other_question=questions[1]), OrderedDict(expected))

    def test_sorted_answers_cardinality(self):
        """ We can sort answer with the sort_answer parameter. """
        alphanumeric = [("abé cé", 2), ("abë-cè", 1), ("dé", 2), ("dë", 1)]
        cardinal = [("abé cé", 2), ("dé", 2), ("abë-cè", 1), ("dë", 1)]
        user_defined = {"dé": 1, "abë-cè": 2, "dë": 3, "abé cé": 4}
        specific = [("dé", 2), ("abë-cè", 1), ("dë", 1), ("abé cé", 2)]
        assert_message = " sorting does not seem to work"
        self.assertEqual(self.sorted_card(group_by_letter_case=True), OrderedDict(cardinal), "default" + assert_message)
        self.assertEqual(
            self.sorted_card(group_by_letter_case=True, sort_answer="alphanumeric"),
            OrderedDict(alphanumeric),
            "alphanumeric" + assert_message,
        )
        self.assertEqual(
            self.sorted_card(group_by_letter_case=True, sort_answer="cardinal"),
            OrderedDict(cardinal),
            "cardinal" + assert_message,
        )
        self.assertEqual(
            self.sorted_card(group_by_letter_case=True, sort_answer=user_defined),
            OrderedDict(specific),
            "user defined" + assert_message,
        )
        other_question_assert_mesage = " when in relation with another question"
        self.assertEqual(
            self.sorted_card(group_by_letter_case=True, other_question=self.questions[1]),
            OrderedDict(
                [
                    ("abé cé", {"left blank": 2}),
                    ("dé", {"left blank": 2}),
                    ("abë-cè", {"left blank": 1}),
                    ("dë", {"left blank": 1}),
                ]
            ),
            "default" + assert_message + other_question_assert_mesage,
        )
        self.assertEqual(
            self.sorted_card(group_by_letter_case=True, sort_answer="alphanumeric", other_question=self.questions[1]),
            OrderedDict(
                [
                    ("abé cé", {"left blank": 2}),
                    ("abë-cè", {"left blank": 1}),
                    ("dé", {"left blank": 2}),
                    ("dë", {"left blank": 1}),
                ]
            ),
            "alphanumeric" + assert_message + other_question_assert_mesage,
        )
        self.assertEqual(
            self.sorted_card(group_by_letter_case=True, sort_answer="cardinal", other_question=self.questions[1]),
            OrderedDict(
                [
                    ("abé cé", {"left blank": 2}),
                    ("dé", {"left blank": 2}),
                    ("abë-cè", {"left blank": 1}),
                    ("dë", {"left blank": 1}),
                ]
            ),
            "cardinal" + assert_message + other_question_assert_mesage,
        )
        self.assertEqual(
            self.sorted_card(group_by_letter_case=True, sort_answer=user_defined, other_question=self.questions[1]),
            OrderedDict(
                [
                    ("dé", {"left blank": 2}),
                    ("abë-cè", {"left blank": 1}),
                    ("dë", {"left blank": 1}),
                    ("abé cé", {"left blank": 2}),
                ]
            ),
            "user defined" + assert_message + other_question_assert_mesage,
        )
