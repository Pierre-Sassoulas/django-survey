# -*- coding: utf-8 -*-
import codecs
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from django.utils.translation import gettext_lazy as _

from survey.exporter.survey2x import Survey2X

LOGGER = logging.getLogger(__name__)


class Survey2Csv(Survey2X):
    @staticmethod
    def line_list_to_string(line):
        """ Write a line in the CSV. """
        new_line = ""
        for i, cell in enumerate(line):
            cell = " ".join(str(cell).split())
            new_line += cell.replace(",", ";")
            if i != len(line) - 1:
                new_line += ","
        return new_line

    @staticmethod
    def get_user_line(question_order, response):
        """ Creating a line for a user """
        LOGGER.debug("\tTreating answer from %s", response.user)
        user_answers = {}
        try:
            user_answers["user"] = response.user.username
        except AttributeError:
            # 'NoneType' object has no attribute 'username'
            user_answers["user"] = _("Anonymous")
        # user_answers[u"entity"] = response.user.entity
        for answer in response.answers.all():
            Survey2Csv.__get_user_line_from_answers(answer, user_answers)
        user_line = []
        for key_ in question_order:
            try:
                user_line.append(user_answers[key_])
            except KeyError:
                user_line.append("")
        return user_line

    @staticmethod
    def __get_user_line_from_answers(answer, user_answers):
        answers = answer.values
        cell = ""
        for i, ans in enumerate(answers):
            if ans is None:
                if settings.USER_DID_NOT_ANSWER is None:
                    raise ImproperlyConfigured("USER_DID_NOT_ANSWER need to be set in your settings file.")
                cell += settings.USER_DID_NOT_ANSWER
            elif i < len(answers) - 1:
                # Separate by a pipe if its not the last
                cell += ans + "|"
            else:
                cell += ans
        LOGGER.debug("\t\t%s : %s", answer.question.pk, cell)
        user_answers[answer.question.pk] = cell

    def get_header_and_order(self):
        """ Creating header.

        :param Survey survey: The survey we're treating. """
        header = [_("user")]  # , u"entity"]
        question_order = ["user"]  # , u"entity" ]
        for question in self.survey.questions.all():
            header.append(question.text)
            question_order.append(question.pk)
        return header, question_order

    def __str__(self):
        csv = []
        if settings.EXCEL_COMPATIBLE_CSV:
            csv.append('"sep=,"')
        header, question_order = self.get_header_and_order()
        csv.append(Survey2Csv.line_list_to_string(header))
        for response in self.survey.responses.all():
            line = Survey2Csv.get_user_line(question_order, response)
            csv.append(Survey2Csv.line_list_to_string(line))
        return "\n".join(csv)

    @staticmethod
    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response.write(codecs.BOM_UTF8)
        filename = ""
        for survey in queryset:
            filename += escape_uri_path(survey.name)
            survey_as_csv = Survey2Csv(survey)
            if len(queryset) == 1:
                response.write(survey_as_csv)
            else:
                response.write("{survey_name}\n".format(survey_name=survey.name))
                response.write(survey_as_csv)
                response.write("\n\n")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(filename)
        return response


Survey2Csv.export_as_csv.short_description = _("export to csv")
