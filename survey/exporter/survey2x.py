# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

import pytz
from django.conf import settings
from django.utils.text import slugify

from survey.models import Survey

LOGGER = logging.getLogger(__name__)


class Survey2X(object):

    """ Abstract class for Survey exporter. """

    def __init__(self, survey=None):
        self._check_survey(survey)
        self.survey = survey

    def _check_survey(self, survey):
        if not isinstance(survey, Survey):
            msg = "Expected Survey not '{}'".format(survey.__class__.__name__)
            raise TypeError(msg)

    def _get_X(self):
        return self.__class__.__name__.split("Survey2")[1].lower()

    def _get_X_dir(self):
        return os.path.join(settings.ROOT, self._get_X())

    def file_name(self):
        """ Return the csv file name for a Survey.

        :param Survey survey: The survey we're treating. """
        file_name = "{}.{}".format(slugify(self.survey.name), self._get_X())
        path = os.path.join(self._get_X_dir(), file_name)
        return path

    @property
    def file_modification_time(self):
        """ Return the modification time of the "x" file. """
        if not os.path.exists(self.file_name()):
            earliest_working_timestamp_for_windows = 86400
            mtime = earliest_working_timestamp_for_windows
        else:
            mtime = os.path.getmtime(self.file_name())
        mtime = datetime.utcfromtimestamp(mtime)
        mtime = mtime.replace(tzinfo=pytz.timezone("UTC"))
        return mtime

    @property
    def latest_answer_date(self):
        """ The date at which the last answer was given"""
        return self.survey.latest_answer_date()

    def need_update(self):
        """ Does a file need an update ?
        If the file was generated before the last answer was given, it needs update. """
        latest_answer_date = self.latest_answer_date
        no_response_at_all = latest_answer_date is None
        if no_response_at_all:
            return False
        file_modification_time = self.file_modification_time
        LOGGER.debug(
            "We %sneed an update because latest_answer_date=%s > "
            "file_modification_time=%s is %s \n",
            "" if latest_answer_date > file_modification_time else "do not ",
            latest_answer_date,
            file_modification_time,
            latest_answer_date > file_modification_time,
        )
        return latest_answer_date >= file_modification_time

    def survey_to_x(self):
        """ Return a string that will be written into a file.

        :rtype String:
        """
        raise NotImplementedError("Please implement survey_to_x()")

    def generate_file(self):
        """ Generate a x file corresponding to a Survey. """

        LOGGER.debug("Exporting survey '%s' to %s", self.survey, self._get_X())
        try:
            with open(self.file_name(), "w", encoding="UTF-8") as f:
                f.write(self.survey_to_x())
            LOGGER.info("Wrote %s in %s", self._get_X(), self.file_name())
        except IOError as exc:
            msg = "Must fix {} ".format(self._get_X_dir())
            msg += "in order to generate {} : {}".format(self._get_X(), exc)
            raise IOError(msg)
