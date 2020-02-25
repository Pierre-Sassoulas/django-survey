# -*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


def in_duration_day():
    return now() + timedelta(days=settings.DEFAULT_SURVEY_PUBLISHING_DURATION)


class Survey(models.Model):

    name = models.CharField(_("Name"), max_length=400)
    description = models.TextField(_("Description"))
    is_published = models.BooleanField(_("Users can see it and answer it"), default=True)
    need_logged_user = models.BooleanField(_("Only authenticated users can see it and answer it"))
    editable_answers = models.BooleanField(_("Users can edit their answers afterwards"), default=True)
    display_by_question = models.BooleanField(_("Display by question"))
    template = models.CharField(_("Template"), max_length=255, null=True, blank=True)
    publish_date = models.DateField(_("Publication date"), blank=True, null=False, default=now)
    expire_date = models.DateField(_("Expiration date"), blank=True, null=False, default=in_duration_day)

    class Meta:
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")

    def __str__(self):
        return self.name

    @property
    def safe_name(self):
        return self.name.replace(" ", "_").encode("utf-8").decode("ISO-8859-1")

    def latest_answer_date(self):
        """ Return the latest answer date.

        Return None is there is no response. """
        min_ = None
        for response in self.responses.all():
            if min_ is None or min_ < response.updated:
                min_ = response.updated
        return min_

    def get_absolute_url(self):
        return reverse("survey-detail", kwargs={"id": self.pk})
