from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from .survey import Survey

try:
    from django.conf import settings

    if settings.AUTH_USER_MODEL:
        UserModel = settings.AUTH_USER_MODEL
    else:
        UserModel = User
except (ImportError, AttributeError):
    UserModel = User


class Response(models.Model):
    """
    A Response object is a collection of questions and answers with a
    unique interview uuid.
    """

    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    updated = models.DateTimeField(_("Update date"), auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="responses")
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, verbose_name=_("User"), null=True, blank=True)
    interview_uuid = models.CharField(_("Interview unique identifier"), max_length=36)

    class Meta:
        verbose_name = _("Set of answers to surveys")
        verbose_name_plural = _("Sets of answers to surveys")

    @property
    def correct_answers_count(self) -> int:
        """
        Returns the number of correct answers in the response.

        Returns:
            int: Number of correct answers
        """
        return sum(1 for answer in self.answers.all() if answer.is_correct)

    @property
    def total_answers_count(self) -> int:
        """
        Returns the total number of answers in the response.

        Returns:
            int: Total number of answers
        """
        return self.answers.count()

    @property
    def correct_answers_percentage(self) -> float:
        """
        Returns the percentage of correct answers.

        Returns:
            float: Percentage of correct answers (0-100)
        """
        total = self.total_answers_count
        if total == 0:
            return 0.0
        return (self.correct_answers_count / total) * 100

    def __str__(self):
        msg = f"Response to {self.survey} by {self.user}"
        msg += f" on {self.created}"
        return msg
