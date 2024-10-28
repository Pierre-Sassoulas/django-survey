import logging
import os
from datetime import datetime
from pathlib import Path

import pytz
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.text import slugify

from survey.models import Survey

LOGGER = logging.getLogger(__name__)


class Survey2X:
    """Abstract class for Survey exporter."""

    def __init__(self, survey=None):
        self._check_survey(survey)
        self.survey = survey
        self.__directory = None

    @staticmethod
    def _check_survey(survey):
        if not isinstance(survey, Survey):
            msg = f"Expected Survey not '{survey.__class__.__name__}'"
            raise TypeError(msg)

    @property
    def mime_type(self):
        return self.__class__.__name__.split("Survey2")[1].lower()

    @property
    def directory(self):
        if self.__directory is None:
            directory_name = f"{self.mime_type.upper()}_DIRECTORY"
            try:
                self.__directory = str(Path(getattr(settings, directory_name)).absolute())
            except AttributeError as e:
                raise ImproperlyConfigured(f"Please define a value for {directory_name} in your settings") from e
        return self.__directory

    @property
    def filename(self):
        return Path(self.directory, f"{slugify(self.survey.name)}.{self.mime_type}")

    @property
    def file_modification_time(self):
        """Return the modification time of the "x" file."""
        if not os.path.exists(self.filename):
            earliest_working_timestamp_for_windows = 86400
            mtime = earliest_working_timestamp_for_windows
        else:
            mtime = os.path.getmtime(self.filename)
        mtime = datetime.utcfromtimestamp(mtime)
        mtime = mtime.replace(tzinfo=pytz.timezone("UTC"))
        return mtime

    @property
    def latest_answer_date(self):
        """The date at which the last answer was given"""
        return self.survey.latest_answer_date()

    def need_update(self):
        """Does a file need an update ?
        If the file was generated before the last answer was given, it needs update."""
        latest_answer_date = self.latest_answer_date
        no_response_at_all = latest_answer_date is None
        if no_response_at_all:
            return not self.__generation_done_once()
        file_modification_time = self.file_modification_time
        LOGGER.debug(
            "We %sneed an update of <%s> because latest_answer_date=%s >= file_modification_time=%s is %s \n",
            "" if latest_answer_date > file_modification_time else "do not ",
            self.survey.name,
            latest_answer_date,
            file_modification_time,
            latest_answer_date > file_modification_time,
        )
        return latest_answer_date >= file_modification_time

    def __generation_done_once(self):
        return not os.path.exists(self.filename)

    def __str__(self):
        """Return a string that will be written into a file.

        :rtype String:
        """
        raise NotImplementedError("Please implement __str__")

    def generate_file(self):
        """Generate a x file corresponding to a Survey."""
        LOGGER.debug("Exporting survey '%s' to '%s'", self.survey, self.mime_type)
        if not self.filename.parent.exists():
            raise NotADirectoryError(self.filename.parent)
        try:
            with open(self.filename, "w", encoding="UTF-8") as f:
                f.write(str(self))
            LOGGER.info("Wrote %s in %s", self.mime_type, self.filename)
        except OSError as exc:
            raise OSError(f"Unable to create <{self.filename}> : {exc} ") from exc
