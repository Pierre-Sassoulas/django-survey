# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _
from django.utils.translation import ungettext


def make_published(modeladmin, request, queryset):
    """
    Mark the given survey as published
    """
    count = queryset.update(is_published=True)
    message = ungettext(
        "%(count)d survey was successfully marked as published.",
        "%(count)d surveys were successfully marked as published",
        count,
    ) % {"count": count}
    modeladmin.message_user(request, message)


make_published.short_description = _("Mark selected surveys as published")
