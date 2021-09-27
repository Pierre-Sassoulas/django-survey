from survey.exporter.tex import ConfigurationBuilder
from survey.models import Survey
from survey.tests.management.test_management import TestManagement


class TestConfigurationBuilder(TestManagement):
    def setUp(self):
        super().setUp()

    def test_init_surveys(self):
        """Only one survey if we init with a survey, all surveys otherwise"""
        all_survey_names = [survey.name for survey in Survey.objects.all()]
        one_survey_conf = ConfigurationBuilder(self.survey)
        self.assertIsInstance(one_survey_conf[self.survey.name], dict)
        for name in all_survey_names:
            if name != self.survey.name:
                self.assertRaises(ValueError, one_survey_conf.get, name)
        all_survey_conf = ConfigurationBuilder()
        for name in all_survey_names:
            self.assertIsInstance(all_survey_conf[name], dict)
