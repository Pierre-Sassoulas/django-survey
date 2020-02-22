from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from survey.exporter.csv.survey2csv import Survey2Csv
from survey.models import Survey

HERE = Path(__file__).parent


class TestIssue70(TestCase):
    fixtures = [Path(HERE, "issue70.json")]
    maxDiff = None

    def setUp(self):
        self.survey = Survey.objects.get(id=4)
        self.s2csv = Survey2Csv(self.survey)

    @override_settings(USER_DID_NOT_ANSWER="Left blank")
    def test_get_survey_as_csv(self):
        header = (
            "user,Email Address,Your Name,Date,STARTS Who? What? Where?,Donations,Books Sold,Your Total Volunteer hours"
            " for this week,Your Volunteer Activities this week.,Included in the above hours; how many of those above "
            "hours were on filing,New Hires,Charitable Donations,Events held What? Where? Products gotten?"
        )
        content = (
            "adminebd,user@example.com,Ed Davison,2020-02-03,Left blank,0,0,8,['Admin'; 'Calls'; 'Events'],0,"
            "Left blank,100,"
        )
        self.expected_content = "{}\n{}".format(header, content)
        self.assertEqual(str(self.s2csv), self.expected_content)

    @override_settings(USER_DID_NOT_ANSWER=None)
    def test_get_survey_as_csv_wrong_settings(self):
        with self.assertRaises(ImproperlyConfigured) as e:
            str(self.s2csv)
        self.assertIn("USER_DID_NOT_ANSWER need to be set", str(e.exception))
