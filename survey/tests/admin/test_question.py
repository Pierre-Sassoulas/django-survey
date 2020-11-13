from unittest import mock

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from survey.admin import QuestionInline
from survey.models.category import Category
from survey.models.survey import Survey


class TestQuestionInlineAdmin(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(
            name="Survey One", description="Survey's Description", need_logged_user=False
        )
        another_survey = Survey.objects.create(
            name="Another Survey", description="Another Survey's Description", need_logged_user=False
        )
        self.category_1 = Category.objects.create(name="First Category", survey=self.survey)
        self.category_2 = Category.objects.create(name="Second Category", survey=self.survey)

        self.another_survey_category = Category.objects.create(name="Another Survey Category", survey=another_survey)

        self.site = AdminSite()
        self.request = mock.Mock()

    def test_question_admin_inline_filter_surveys_category(self):
        question_admin = QuestionInline(Survey, self.site)
        formset = question_admin.get_formset(self.request, self.survey)
        qs = formset.form.base_fields["category"].queryset

        self.assertEqual(qs.count(), 2)
        self.assertNotIn(self.another_survey_category, qs)

    def test_question_admin_inline_filter_no_surveys_yet(self):
        self.survey.delete()
        self.another_survey_category.delete()
        self.survey = None

        question_admin = QuestionInline(Survey, self.site)
        formset = question_admin.get_formset(self.request, self.survey)
        qs = formset.form.base_fields["category"].queryset

        self.assertEqual(qs.count(), 0)
