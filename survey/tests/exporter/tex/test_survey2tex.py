# -*- coding: utf-8 -*-

from pathlib import Path

from survey.exporter.tex.configuration import Configuration
from survey.exporter.tex.survey2tex import Survey2Tex
from survey.models import Survey
from survey.tests.management.test_management import TestManagement


class TestSurvey2Tex(TestManagement):
    def setUp(self):
        TestManagement.setUp(self)
        conf = Configuration(Path(self.conf_dir, "test_conf.yaml"))
        self.generic = Survey2Tex(self.survey, conf)
        self.test_survey = Survey.objects.get(name="Test survëy")
        self.specific = Survey2Tex(self.test_survey, conf)

    def test_get_survey_as_tex(self):
        """ The content of the tex is correct. """
        generic = str(self.generic)
        should_contain = [
            "documentclass[11pt]{article}",
            "title{My title}",
            "Test management footer.",
            "Aèbc?",
            "Bècd?",
            "Cède?",
            "",
        ]
        for text in should_contain:
            self.assertIn(text, generic)
        specific = str(self.specific)
        should_contain = [
            "documentclass[11pt]{report}",
            "title{My title}",
            "This is the footer.",
            "{Lorem ipsum dolor sit amët",
            "adipiscing}  elit.'",
            "with 'K.' standing for 'Yës'",
            "'Nah' standing for 'No' or 'Whatever'",
        ]
        for text in should_contain:
            self.assertIn(text, specific)

    def test_custom_class_fail_import(self):
        """ We have an error message if the type is impossible to import. """
        conf = Configuration(Path(self.conf_dir, "custom_class_doesnt_exists.yaml"))
        self.test_survey = Survey.objects.get(name="Test survëy")
        fail_import = str(Survey2Tex(self.test_survey, conf))
        should_contain = [
            "could not render",
            "not a standard type",
            "importable valid Question2Tex child class",
            "'raw'",
            "'sankey'",
            "'pie'",
            "'cloud'",
            "'square'",
            "'polar'",
        ]
        for text in should_contain:
            self.assertIn(text, fail_import)
