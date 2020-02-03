# -*- coding: utf-8 -*-

import sys

from operator import itemgetter 


from django.core.management.base import BaseCommand

from survey.models import Survey
from survey.models.question import Question


class SurveyCommand(BaseCommand):

    requires_system_checks = False

    def add_arguments(self, parser):
        help_text = "The {}s of the {}s we want to generate. Default is None."
        parser.add_argument("--survey-all", action="store_true", help="Use to generate all surveys. Default is False.")
        parser.add_argument("--survey-id", nargs="+", type=int, help=help_text.format("primary key", "survey"))
        parser.add_argument("--survey-name", nargs="+", type=str, help=help_text.format("name", "survey"))
        parser.add_argument("--survey-latest", action="store_true", help="Use to generate the latest survey. Default is False.")
        parser.add_argument(
            "--question-all", action="store_true", help="Use to generate all questions. Default is False."
        )
        parser.add_argument("--question-id", nargs="+", type=int, help=help_text.format("primary key", "question"))
        parser.add_argument("--question-text", nargs="+", type=str, help=help_text.format("text", "question"))

    def raise_value_error(self, error_type, value):
        """ Raise a ValueError with a clean error message in python 2.7 and 3.
        :param string value: the attempted value. """
        if error_type in ["question-id", "question-text"]:
            base = "--question-id {} / --question-text '{}'\n"
            valids = [(q.pk, q.text) for q in Question.objects.all()]
        elif error_type in ["survey-name", "survey-id"]:
            base = "--survey-id {} / --survey-name '{}'\n"
            valids = [(s.pk, s.name) for s in Survey.objects.all()]
        msg = "You tried to get --{} '{}' ".format(error_type, value)
        if valids:
            msg += "but is does not exists. Possibles values :\n"
            for pk, name in valids:
                msg += base.format(pk, name)
            msg = msg[:-1]  # Remove last \n
        else:
            msg += "but there is nothing in the database."
        # Compatibility for python 2.7 and 3
        # See: https://stackoverflow.com/questions/46076279/
        if sys.version_info.major == 2:  # pragma: no cover
            raise ValueError(msg.encode("utf-8"))
        # pragma: no cover
        raise ValueError(msg)

    def check_mutually_exclusive(self, opts):
        """ We could use the ArgParse option for this, but the case is
        simple enough to be treated this way. """

        all_questions = opts.get("question_all")
        some_questions = opts.get("question_text") or opts.get("question_id")
        all_surveys = opts.get("survey_all")
        some_surveys = opts.get("survey_name") or opts.get("survey_id") 
        error_msg = "You cannot generate only some {} to generate everything. Use one or the other."
        if all_questions and some_questions:
            sys.exit(
                error_msg.format("questions with '--question-id' or --question-text' while also using '--question-all'")
            )
        if all_surveys and some_surveys:
            sys.exit(error_msg.format("survey with '--survey-id' or '--survey-name' while also using '--survey-all'"))

    def check_nothing_at_all(self, options):
        at_least_a_question = options.get("question_all") or options.get("question_text") or options.get("question_id")
        at_least_a_survey = options.get("survey_all") or options.get("survey_name") or options.get("survey_id") or options.get("survey_latest")
        if not at_least_a_question and not at_least_a_survey:
            sys.exit(
                "Nothing to do, add at least one of the following options :\n"
                "'--question-id', '--question-text' '--question-all',"
                "'--survey-id', '--survey-name', '--survey-all'."
            )

    def handle(self, *args, **options):
        self.check_mutually_exclusive(options)
        self.check_nothing_at_all(options)
        self.set_questions(options)
        self.set_surveys(options)

    def set_surveys(self, options):
        if options.get("survey_all"):
            self.surveys = Survey.objects.all()
        else:
            self.surveys = []
            if options.get("survey_name"):
                for survey_name in options["survey_name"]:
                    try:
                        self.surveys.append(Survey.objects.get(name=survey_name))
                    except Survey.DoesNotExist:
                        self.raise_value_error("survey-name", survey_name)
            if options.get("survey_id"):
                for survey_id in options["survey_id"]:
                    try:
                        self.surveys.append(Survey.objects.get(pk=survey_id))
                    except Survey.DoesNotExist:
                        self.raise_value_error("survey-id", survey_id)
            if options.get("survey_latest"):
                valids = [(s.pk, s.name) for s in Survey.objects.all()]
                survey_id = max(valids, key = itemgetter(0))[0]
                try:
                    self.surveys.append(Survey.objects.get(pk=survey_id))
                except Survey.DoesNotExist:
                    self.raise_value_error("survey-id", survey_id)




    def set_questions(self, options):
        if options.get("question_all"):
            self.questions = Question.objects.all()
        else:
            self.questions = []
            if options.get("question_text"):
                for question_text in options["question_text"]:
                    try:
                        self.questions.append(Question.objects.get(text=question_text))
                    except Question.DoesNotExist:
                        self.raise_value_error("question-text", question_text)
            if options.get("question_id"):
                for question_id in options["question_id"]:
                    try:
                        self.questions.append(Question.objects.get(pk=question_id))
                    except Question.DoesNotExist:
                        self.raise_value_error("question-id", question_id)
