import os

from django.core.management import call_command

from survey.models.survey import Survey
from survey.tests.management.test_management import TestManagement


class TestGenerateTexConfiguration(TestManagement):
    def assert_command_create_file(self, arg=None, value=None):
        file = "output"
        if arg and value:
            call_command("generatetexconf", file, arg, value)
            self.assertTrue(os.path.exists(file))
            if os.path.exists(file):
                os.remove(file)
        else:
            surveys = Survey.objects.all()
            output_files = [file + str(i) for i, _ in enumerate(surveys)]
            call_command("generatetexconf", "--survey-all", *output_files)
            for path in output_files:
                self.assertTrue(os.path.exists(path))
                if os.path.exists(path):
                    os.remove(path)

    def test_handle(self):
        self.assert_command_create_file()
        self.assert_command_create_file("--survey-name", "Test survëy")
        self.assert_command_create_file("--survey-id", 1)

    def test_error_message(self):
        self.assertRaises(ValueError, call_command, "generatetexconf", "output", "--survey-id", 25)
        self.assertRaises(SystemExit, call_command, "generatetexconf", "output", survey_all=True)
        self.assertRaises(ValueError, call_command, "generatetexconf", "output", "--survey-name", "Do not exists")
