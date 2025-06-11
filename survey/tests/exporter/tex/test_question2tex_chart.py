from django.conf import settings

from survey.exporter.tex.question2tex_chart import Question2TexChart
from survey.tests.management.test_management import TestManagement


class TestQuestion2TexChart(TestManagement):
    def test_get_tex(self):
        """The header and order of the question is correct."""
        question = self.survey.questions.get(text="Aèbc?")
        self.assertIsNotNone(Question2TexChart(question).tex())
        color = {}
        groups = {"1é": ["1e", "1é", "1ë"], "2é": ["2e", "2é", "2ë"], "3é": ["3e", "3é", "3ë"]}
        color["1b"] = "green!80"
        color["1a"] = "cyan!50"
        color["1é"] = "red!80"
        chart = Question2TexChart(question, color=color, group_together=groups).tex()
        expected_color = settings.SURVEY_DEFAULT_PIE_COLOR
        self.assertIn(expected_color, chart)
        color["1"] = "yellow!70"
        chart = Question2TexChart(
            question, color=color, group_together=groups, sort_answer={"1b": 1, "1a": 2, "1": 3, "1é": 4}
        ).tex()
        expected_colors = ["red!80", "yellow!70", "cyan!50", "green!80"]
        for expected_color in expected_colors:
            self.assertIn(expected_color, chart)
        self.assertIn(
            "1/1b,\n            1/1a,\n            1/1,\n            4/1é",
            chart,
            "User defined sort does not seem to works.",
        )
        chart = Question2TexChart(question, color=color, group_together=groups, sort_answer="cardinal").tex()
        self.assertIn(
            "4/1\xe9,\n            1/Left blank,\n            1/1,\n            1/1a,\n            1/1b",
            chart,
            f"Cardinal sort does not seem to works. {chart}",
        )
        chart = Question2TexChart(question, color=color, group_together=groups, sort_answer="alphanumeric").tex()
        self.assertIn(
            "1/1,\n            1/1a,\n            1/1b,\n            4/1é",
            chart,
            f"Alphanumeric sort does not seem to works.. {chart}",
        )
        chart = Question2TexChart(question, group_together=groups, sort_answer="unknown_option").tex()
        self.assertIn(
            "4/1\xe9,\n            1/Left blank,\n            1/1,\n            1/1a,\n            1/1b",
            chart,
            f"Default behavior does not sort by cardinality. {chart}",
        )

    def test_cloud_tex(self):
        """We can create a cloud chart."""
        question = self.survey.questions.get(text="Aèbc?")
        self.assertIsNotNone(Question2TexChart(question, type="cloud").tex())

    def test_get_caption(self):
        """We can create a filtered chart with a proper caption."""
        question = self.survey.questions.get(text="Cède?")

        def get_options(
            min_cardinality=0,
            filter=None,
            group_together=None,
            group_by_slugify=None,
            group_by_lettercase=None,
            cardinality=None,
        ):
            """Permit to have default options while defining specific options
            explicitely."""
            if filter is None:
                filter = {}
            if group_together is None:
                group_together = {}
            return {
                "question": question,
                "min_cardinality": min_cardinality,
                "filter": filter,
                "group_together": group_together,
                "group_by_slugify": group_by_slugify,
                "group_by_lettercase": group_by_lettercase,
                # We do not have cardinality in get_caption but we want to be
                # able to change the question cardinality
                "cardinality": cardinality,
            }

        def get_result(**options):
            """Return the result of get_caption using options.
            If cardinality is set we change the cardinality of the question."""
            q2c = Question2TexChart(**options)
            if options.get("cardinality") is not None:
                q2c.cardinality = options.get("cardinality")
            return q2c.get_caption()

        options = get_options(min_cardinality=2)
        self.assertIn("2 respondent or more", get_result(**options))
        options = get_options(filter=["Toto"])
        self.assertIn("excluding 'Toto' ", get_result(**options))
        options = get_options(filter=["Toto", "Titi"])
        self.assertIn("excluding 'Toto', and 'Titi' ", get_result(**options))
        options = get_options(filter=["Toto", "Titi", "Tutu"])
        self.assertIn("excluding 'Toto', 'Titi', and 'Tutu' ", get_result(**options))
        options = get_options(filter=["Toto", ""], cardinality={"Toto": 2, "": 1})
        self.assertIn("excluding 'Toto', and 'Left blank' ", get_result(**options))
        options = get_options(group_together={"No": ["No", "Maybe"], "Yes": ["Kay"]}, cardinality={"No": 2})
        self.assertIn("with 'No' standing for 'No' or 'Maybe'.", get_result(**options))
        options = get_options(group_together={"No": ["No", "Maybe"], "Yes": ["Kay"]}, cardinality={"No": 2, "Yes": 1})
        result = get_result(**options)
        self.assertIn("'Yes' standing for 'Kay'", result)
        self.assertIn("'No' standing for 'No' or 'Maybe'", result)
        # We do not signal if group_together is just a placeholder.
        options = get_options(
            group_together={"No": ["No", "Nö", "NO"]},
            group_by_slugify=True,
            group_by_lettercase=True,
            cardinality={"No": 2},
        )
        self.assertIn("Repartition of answers for the question 'Cède?'.", get_result(**options))
        options = get_options(group_together={"Yes": ["Kay"]}, cardinality={"No": 2})
        self.assertIn("Repartition of answers for the question 'Cède?'.", get_result(**options))

    def test_no_results(self):
        """We manage having no result at all."""
        question = self.survey.questions.get(text="Dèef?")
        self.assertIn("No answers for this question.", Question2TexChart(question).tex())
