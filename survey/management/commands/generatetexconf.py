# -*- coding: utf-8 -*-

from survey.exporter.tex import ConfigurationBuilder
from survey.management.survey_command import SurveyCommand


class Command(SurveyCommand):

    """
        See the "help" var.
    """

    help = """This command permit to generate the latex configuration in order
    to manage the survey report generation. """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("output", nargs="+", type=str, help="Output prefix.")

    def write_conf(self, name, conf):
        file_ = open(name, "w", encoding="UTF-8")
        file_.write(str(conf))
        file_.close()

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        output = options["output"]
        if len(output) != len(self.surveys):
            exit(
                "You want to generate {} surveys ".format(len(self.surveys))
                + "but you only gave {} output names".format(len(output))
            )
        for i, survey in enumerate(self.surveys):
            conf = ConfigurationBuilder(survey)
            self.write_conf(output[i], conf)
