from django.utils import timezone
from django.views.generic import TemplateView

from survey.models import Survey


class IndexView(TemplateView):
    template_name = "survey/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        surveys = Survey.objects.filter(is_published=True, expire_date__gte=today, publish_date__lte=today)
        if not self.request.user.is_authenticated:
            surveys = surveys.filter(need_logged_user=False)
        context["surveys"] = surveys
        return context
