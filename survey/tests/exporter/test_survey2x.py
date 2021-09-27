import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from django.test.utils import override_settings

from survey.exporter.survey2x import Survey2X
from survey.tests.management.test_management import TestManagement

LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).parent.parent.parent


class Survey2Survey(Survey2X):
    def __str__(self):
        pass


LONG_TIME_AGO = datetime(1990, 1, 1, 0, 0, 0)
SHORT_TIME_AGO = datetime(2000, 1, 1, 0, 0, 0)
RIGHT_NOW = datetime(2010, 1, 1, 0, 0, 0)


@override_settings(SURVEY_DIRECTORY=Path(ROOT, "survey"))
class TestSurvey2X(TestManagement):
    def setUp(self):
        super().setUp()
        self.virtual_survey2x = Survey2X(self.survey)
        self.actual_survey2x = Survey2Survey(self.survey)
        self.expected_actual = Path(ROOT, "survey", "test-management-survey.survey")
        self.expected_virtual = Path(ROOT, "x", "test-management-survey.x")

    def get_fail_info(self, survey2x):
        msg = f"\nLatest answer date :     {survey2x.latest_answer_date}"
        msg += f"\nFile modification time : {survey2x.file_modification_time}"
        return msg

    def test_str(self):
        self.assertRaises(NotImplementedError, self.virtual_survey2x.__str__)

    @override_settings(X_DIRECTORY=Path(ROOT, "x"))
    def test_filename(self):
        self.assertEqual(self.actual_survey2x.filename, self.expected_actual)
        self.assertEqual(self.virtual_survey2x.filename, self.expected_virtual)

    def test_initially_need_update(self):
        self.assertTrue(
            self.actual_survey2x.need_update(),
            "No file exported and the survey "
            "contain response : we should need an update. "
            "{}".format(self.get_fail_info(self.actual_survey2x)),
        )

    @patch.object(Survey2Survey, "file_modification_time", RIGHT_NOW)
    @patch.object(Survey2Survey, "latest_answer_date", LONG_TIME_AGO)
    def test_need_update_after_generation(self):
        self.assertFalse(
            self.actual_survey2x.need_update(),
            "We exported the file and there"
            " is no new response, we should not need an update. "
            "{}".format(self.get_fail_info(self.actual_survey2x)),
        )

    @patch.object(Survey2Survey, "file_modification_time", LONG_TIME_AGO)
    @patch.object(Survey2Survey, "latest_answer_date", RIGHT_NOW)
    def test_need_update_after_new_response(self):
        self.assertTrue(
            self.actual_survey2x.need_update(),
            "We exported the file but there"
            " is a new response, we should need an update. "
            "{}".format(self.get_fail_info(self.actual_survey2x)),
        )
