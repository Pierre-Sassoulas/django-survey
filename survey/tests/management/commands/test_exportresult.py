# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.core.management import call_command
from django.utils.text import slugify

from survey.tests.management.test_management import TestManagement


class TestExportresult(TestManagement):

    """ Permit to check if export result is working as intended. """

    def get_csv_path(self, survey_name):
        csv_name = "{}.csv".format(slugify(survey_name))
        return os.path.join(settings.CSV_DIR, csv_name)

    def get_file_content(self, path):
        file_ = open(path, encoding="UTF-8")
        content = file_.read()
        file_.close()
        return content

    def test_no_options(self):
        """ If no options are given there are warning and error messages. """
        self.assertRaises(SystemExit, call_command, "exportresult")
        call_command("exportresult", "--pdf", survey_id="1")
        call_command("exportresult", "--pdf", "--force", survey_id="1")

    def test_handle(self):
        """ The custom command export result create the right csv file. """
        self.maxDiff = None
        first_csv = self.get_csv_path(self.test_managament_survey_name)
        second_csv = self.get_csv_path("Test survëy")
        # Force to regenerate the csv, we want to test something not optimize
        # computing time.
        if os.path.exists(first_csv):
            os.remove(first_csv)
        if os.path.exists(second_csv):
            os.remove(second_csv)
        call_command(
            "exportresult",
            "--survey-all",
            "--tex",
            "--csv",
            "--force",
            configuration_file=self.test_conf_path,
        )
        self.assertMultiLineEqual(
            self.expected_content, self.get_file_content(first_csv)
        )
        expected = """\
user,Lorem ipsum dolor sit amët; <strong> consectetur </strong> adipiscing \
elit.,Ipsum dolor sit amët; <strong> consectetur </strong> adipiscing elit.,\
Dolor sit amët; <strong> consectetur</strong> adipiscing elit.,Lorem ipsum\
 dolor sit amët; consectetur<strong> adipiscing </strong> elit.,Ipsum dolor \
sit amët; consectetur <strong> adipiscing </strong> elit.,Dolor sit amët; \
consectetur<strong> adipiscing</strong> elit.
pierre,Yës|Maybe,No,Text for a response,,2,No|Whatever
ps250112,Yës,Yës,,,1,Yës"""
        self.assertMultiLineEqual(expected, self.get_file_content(second_csv))
