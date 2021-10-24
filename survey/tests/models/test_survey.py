from datetime import date

from django.core.validators import URLValidator
from django.utils.timezone import now

from survey.tests.models import BaseModelTest


class TestSurvey(BaseModelTest):
    def test_unicode(self):
        """Unicode generation."""
        self.assertIsNotNone(str(self.survey))

    def test_questions(self):
        """Recovering a list of questions from a survey."""
        questions = self.survey.questions.all()
        self.assertEqual(len(questions), len(self.data))

    def test_absolute_url(self):
        """Absoulte url is not None and do not raise error."""
        self.assertIsNotNone(self.survey.get_absolute_url())

    def test_latest_answer(self):
        """the lastest answer date is returned."""
        self.assertIsInstance(self.survey.latest_answer_date(), date)

    def test_publish_date(self):
        """the pblish date must be None or datetime date instance."""
        self.assertIsInstance(self.survey.publish_date, date)

    def test_expiration_date(self):
        """expirationdate must be datetime date instance or None"""
        self.assertIsInstance(self.survey.expire_date, date)

    def test_expiration_date_is_in_future(self):
        """by default the expiration should be a week in the future"""
        self.assertGreater(self.survey.expire_date, now())

    def test_redirect_url(self):
        self.assertIsNone(URLValidator()(self.survey.redirect_url))
