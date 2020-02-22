# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.test.utils import override_settings

from survey.exporter.csv.survey2csv import Survey2Csv
from survey.tests.management.test_management import TestManagement


@staticmethod
def raise_io_exc():
    raise IOError()


class TestSurvey2Csv(TestManagement):

    """ Permit to check if export result is working as intended. """

    def setUp(self):
        TestManagement.setUp(self)
        self.maxDiff = None
        self.s2csv = Survey2Csv(self.survey)

    def test_get_header_and_order(self):
        """ The header and order of the question is correct. """
        header, order = self.s2csv.get_header_and_order()
        self.assertEqual(header, self.expected_header)
        self.assertEqual(len(order), len(self.expected_header))

    def test_get_survey_as_csv(self):
        """ The content of the CSV is correct. """
        self.assertEqual(str(self.s2csv), self.expected_content)

    @override_settings(EXCEL_COMPATIBLE_CSV=True)
    def test_get_survey_excel_compatible(self):
        self.assertEqual(str(self.s2csv), '"sep=,"\n' + self.expected_content)

    @patch.object(Survey2Csv, "file_name", raise_io_exc)
    def test_dir_not_exists(self):
        """ We raise an IoError if the directory does not exists. """
        self.assertRaises(IOError, self.s2csv.generate_file)

    def test_not_a_survey(self):
        """ TypeError raised when the object is not a survey. """
        self.assertRaises(TypeError, Survey2Csv, "Not a survey")

    def test_filename(self):
        """ Filename is not an unicode object or os.path and others fail. """
        name = self.s2csv.file_name()
        self.assertIn("csv", name)
        self.assertIn("test-management-survey.csv", name)
