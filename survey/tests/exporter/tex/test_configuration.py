# -*- coding: utf-8 -*-

from pathlib import Path

from survey.exporter.tex.configuration import Configuration
from survey.models.survey import Survey
from survey.tests.management.test_management import TestManagement


class TestConfiguration(TestManagement):
    def setUp(self):
        TestManagement.setUp(self)
        self.conf = Configuration(self.test_conf_path)
        self.default = Configuration()
        self.ts_conf = self.conf.get(survey_name="Test survëy")
        self.qts_conf = self.conf.get(
            survey_name="Test survëy", question_text="Dolor sit amët, consectetur<strong>  adipiscing</strong>  elit."
        )
        self.qts_expected_conf = {"min_cardinality": 0, "type": "cloud", "radius": 1, "text": "inside"}

    def test_name_doesnt_exists(self):
        """ Value error raised when the name does not exists. """
        name = "This survey does not exists"
        path = Path(self.conf_dir, "name_doesnt_exists.yaml")
        conf = Configuration(path)
        self.assertIsNotNone(conf.get(survey_name=name))
        Survey.objects.create(name=name, is_published=True, need_logged_user=True, display_method=Survey.BY_QUESTION)
        conf = Configuration(path)
        self.assertIsNotNone(conf.get(survey_name=name))

    def test_str(self):
        """ No error for str """
        self.assertIsNotNone(str(self.conf))

    def test_wrong_type(self):
        """ If we give the wrong type for survey_name we get a TypeError. """
        self.assertRaises(TypeError, self.conf.get, survey_name=self.survey)

    def test_no_value_defined(self):
        """ We raise a value error if there is nothing at all for a Survey."""
        path = Path(self.conf_dir, "no_value_defined.yaml")
        self.assertRaises(ValueError, Configuration, path)

    def test_use_default(self):
        """ If the value is undefined for a survey we use default. """
        short_survey_conf = self.conf.get(survey_name="Short Survëy")
        self.assertEqual(short_survey_conf.get("document_class"), "article")

    def test_change_default(self):
        """ If a value is set in a survey, the default is changed. """
        ss_conf = self.conf["Short Survëy"]
        self.assertEqual(ss_conf.get("footer"), "Short survey footer.")
        self.assertEqual(ss_conf.get("document_class"), "article")
        # Test Management Survëy conf
        tm_survey = Survey.objects.get(name="Test Management Survëy")
        tm_conf = self.conf.get(survey_name=tm_survey.name)
        self.assertEqual(tm_conf.get("footer"), "Test management footer.")
        self.assertEqual(tm_conf.get("document_class"), "article")
        self.assertEqual(self.conf.get("footer", "Test survëy"), "This is the footer.")
        self.assertEqual(self.conf.get(key="document_class", survey_name="Test survëy"), "report")
        self.assertEqual(self.conf.get("footer"), "This is the footer.")
        self.assertEqual(self.conf.get("document_class"), "article")

    def test_get_questions(self):
        """ We have something coherent when we get by question_text. """
        self.assertEqual(self.ts_conf["chart"]["min_cardinality"], 0)
        self.assertEqual(self.ts_conf["chart"]["type"], "pie")
        self.assertEqual(self.ts_conf["chart"]["radius"], 3)
        self.assertEqual(self.ts_conf["chart"]["text"], "legend")
        for key, value in list(self.qts_expected_conf.items()):
            self.assertEqual(self.qts_conf["chart"][key], value)

    def test_get_question_multiple_charts(self):
        """ We have set multiple charts when we get by question text. """
        self.assertEqual(self.ts_conf["multiple_charts"], None)
        self.assertEqual(self.ts_conf["multiple_chart_type"], "subsubsection")
        self.assertEqual(self.qts_conf["multiple_chart_type"], "subsubsection")
        qts_charts = ["Sub Sub Section with radius=3", "Sub Sub Section with text=pin"]
        qts_charts.sort()
        qts_mc_results = list(self.qts_conf.get("multiple_charts").keys())
        qts_mc_results.sort()
        self.assertEqual(qts_mc_results, qts_charts)
        for chart in qts_charts:
            for key, expected_value in list(self.qts_expected_conf.items()):
                value = self.qts_conf["multiple_charts"][chart][key]
                if chart == "Sub Sub Section with radius=3" and key == "radius":
                    expected_value = 3
                elif chart == "Sub Sub Section with text=pin" and key == "text":
                    expected_value = "pin"
                self.assertEqual(
                    value,
                    expected_value,
                    "Expected '{}' for '{}' in '{}' and got '{}'".format(expected_value, key, chart, value),
                )

    def test_value_doesnt_exists(self):
        """ Get when a value does not exists. """
        self.assertRaises(ValueError, self.conf.get, key="noexists")
        self.assertRaises(ValueError, self.conf.get, survey_name="Test survëy", key="noexists")
        self.assertRaises(
            ValueError,
            self.conf.get,
            survey_name="Test survëy",
            question_text="Dolor sit amët, consectetur<strong>  adipiscing</strong>  elit.",
            key="noexists",
        )
