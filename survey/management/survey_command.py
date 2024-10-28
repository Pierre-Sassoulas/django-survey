import sys
from operator import itemgetter

from django.core.management.base import BaseCommand

from survey.models import Survey
from survey.models.question import Question


class SurveyCommand(BaseCommand):
    requires_system_checks = []

    def add_arguments(self, parser):
        help_text = "The {}s of the {}s we want to generate. Default is None."
        parser.add_argument("--survey-all", action="store_true", help="Use to generate all surveys. Default is False.")
        parser.add_argument("--survey-id", nargs="+", type=int, help=help_text.format("primary key", "survey"))
        parser.add_argument("--survey-name", nargs="+", type=str, help=help_text.format("name", "survey"))
        parser.add_argument(
            "--survey-latest", action="store_true", help="Use to generate the latest survey. Default is False."
        )
        parser.add_argument(
            "--question-all", action="store_true", help="Use to generate all questions. Default is False."
        )
        parser.add_argument("--question-id", nargs="+", type=int, help=help_text.format("primary key", "question"))
        parser.add_argument("--question-text", nargs="+", type=str, help=help_text.format("text", "question"))

    @staticmethod
    def raise_value_error(error_type, value):
        """Raise a ValueError with a clean error message in python 2.7 and 3.
        :param string value: the attempted value."""
        valid_texts = []
        base = "--question-id {} / --question-text '{}'\n"
        if error_type in ["question-id", "question-text"]:
            valid_texts = [(q.pk, q.text) for q in Question.objects.all()]
        elif error_type in ["survey-name", "survey-id"]:
            base = "--survey-id {} / --survey-name '{}'\n"
            valid_texts = [(s.pk, s.name) for s in Survey.objects.all()]
        msg = f"You tried to get --{error_type} '{value}' "
        if valid_texts:
            msg += "but is does not exists. Possibles values :\n"
            for primary_key, name in valid_texts:
                msg += base.format(primary_key, name)
            msg = msg[:-1]  # Remove last \n
        else:
            msg += "but there is nothing in the database."
        # Compatibility for python 2.7 and 3
        # See: https://stackoverflow.com/questions/46076279/
        if sys.version_info.major == 2:  # pragma: no cover
            raise ValueError(msg.encode("utf-8"))
        # pragma: no cover
        raise ValueError(msg)

    @staticmethod
    def check_mutually_exclusive(opts):
        """We could use the ArgParse option for this, but the case is simple enough to be treated this way."""
        all_questions = opts.get("question_all")
        some_questions = opts.get("question_text") or opts.get("question_id")
        all_surveys = opts.get("survey_all")
        some_surveys = opts.get("survey_name") or opts.get("survey_id") or opts.get("survey_latest")
        error_msg = "You cannot generate only some {} to generate everything. Use one or the other."
        if all_questions and some_questions:
            sys.exit(
                error_msg.format("questions with '--question-id' or --question-text' while also using '--question-all'")
            )
        if all_surveys and some_surveys:
            sys.exit(error_msg.format("survey with '--survey-id' or '--survey-name' while also using '--survey-all'"))

    @staticmethod
    def check_nothing_at_all(options):
        at_least_a_question = options.get("question_all") or options.get("question_text") or options.get("question_id")
        at_least_a_survey = (
            options.get("survey_all")
            or options.get("survey_name")
            or options.get("survey_id")
            or options.get("survey_latest")
        )
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
        #  pylint: disable=attribute-defined-outside-init
        self.surveys = []
        if options.get("survey_all"):
            self.surveys = Survey.objects.all()
        else:
            names = options.get("survey_name") or []
            for survey_name in names:
                self.__add_survey_by_name(survey_name)
            ids = options.get("survey_id") or []
            for survey_id in ids:
                self.__add_survey_by_id(survey_id)
            if options.get("survey_latest"):
                survey_id = self.__get_latest_id()
                self.__add_survey_by_id(survey_id)

    @staticmethod
    def __get_latest_id():
        valids = [(s.pk, s.name) for s in Survey.objects.all()]
        return max(valids, key=itemgetter(0))[0]

    def __add_survey_by_id(self, survey_id):
        try:
            self.surveys.append(Survey.objects.get(pk=survey_id))
        except Survey.DoesNotExist:
            self.raise_value_error("survey-id", survey_id)

    def __add_survey_by_name(self, survey_name):
        try:
            self.surveys.append(Survey.objects.get(name=survey_name))
        except Survey.DoesNotExist:
            self.raise_value_error("survey-name", survey_name)

    def set_questions(self, options):
        #  pylint: disable=attribute-defined-outside-init
        self.questions = []
        if options.get("question_all"):
            self.questions = Question.objects.all()
        else:
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
