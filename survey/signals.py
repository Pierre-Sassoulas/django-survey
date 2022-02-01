import django.dispatch

# providing_args=["instance", "data"]
survey_completed = django.dispatch.Signal()
