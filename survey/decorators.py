import logging
from functools import wraps

from django.contrib import messages
from django.shortcuts import Http404, get_object_or_404, redirect, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from survey.models import Survey

LOGGER = logging.getLogger(__name__)


def survey_available(func):
    """
    Checks if a survey is available (published and not expired).

    Use this as a decorator for view functions.
    """

    @wraps(func)
    def survey_check(self, request, *args, **kwargs):
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), is_published=True, id=kwargs["id"]
        )
        if not survey.is_published:
            raise Http404
        if survey.expire_date < timezone.now().date():
            msg = "Survey is not published anymore. It was published until: '%s'."
            LOGGER.warning(msg, survey.expire_date)
            messages.warning(request, _("This survey has expired for new submissions."))
            return redirect(reverse("survey-list"))
        if survey.publish_date > timezone.now().date():
            msg = "Survey is not yet published. It is due: '%s'."
            LOGGER.warning(msg, survey.publish_date)
            raise Http404
        return func(self, request, *args, **kwargs, survey=survey)

    return survey_check
