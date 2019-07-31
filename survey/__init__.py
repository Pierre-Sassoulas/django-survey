def set_default_settings():
    try:
        from django.conf import settings
        from . import settings as app_settings

        for setting in dir(app_settings):
            if setting == "CHOICES_SEPARATOR":
                if not hasattr(settings, setting):
                    setattr(settings, setting, getattr(app_settings, setting))
    except ImportError:
        pass


set_default_settings()
