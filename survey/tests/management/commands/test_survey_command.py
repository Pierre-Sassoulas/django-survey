from django.core.management import call_command

from survey.management.survey_command import SurveyCommand
from survey.tests.base_test import BaseTest


class TestSurveyCommand(BaseTest):
    def setUp(self):
        self.handle = SurveyCommand().handle

    def test_questions(self):
        """We can define questions."""
        self.assertRaises(ValueError, self.handle, question_text=["Do not exists"])
        self.assertRaises(ValueError, self.handle, question_id=[4242])

    def test_surveys(self):
        """We can define surveys."""
        self.assertRaises(ValueError, self.handle, survey_name=["Do not exists"])
        self.assertRaises(ValueError, self.handle, survey_id=[1, 4242])

    def test_empty_database(self):
        """Specific message when db is empty."""
        call_command("flush", "--noinput")
        self.assertRaises(ValueError, self.handle, survey_id=[1])

    def test_mutually_exclusive(self):
        """Some options are mutually exclusive."""
        self.assertRaises(SystemExit, self.handle, question_all=True, question_text=["Lorem?"])
        self.assertRaises(SystemExit, self.handle, question_all=True, question_id=[1])
        self.assertRaises(SystemExit, self.handle, survey_all=True, survey_name=["Test survëy"])
        self.assertRaises(SystemExit, self.handle, survey_all=True, survey_id=[1])

    def test_at_least_something(self):
        """We warn the user if nothing will be generated."""
        self.assertRaises(SystemExit, self.handle)
