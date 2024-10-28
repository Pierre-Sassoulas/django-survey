from survey.models import Survey

from .configuration import Configuration


class ConfigurationBuilder(Configuration):
    """
    Permit to create serializable uninitialized configuration easily.
    We just use the default dict for a Builder, the user will be able to
    modify value from the default.

    We delete unwanted survey in self._conf in order to print
    only what the user want.
    """

    def __init__(self, survey=None):
        """Initialize a configuration file.

        :param Survey survey: If survey is defined we generate configuration
        only for this survey."""
        super().__init__(self.DEFAULT_PATH)
        self._init_default()
        if survey:
            for other_survey in Survey.objects.all():
                unwanted_survey = survey.name != other_survey.name
                if unwanted_survey:
                    del self._conf[other_survey.name]

    def _init_default(self):
        """Return the default configuration."""
        default_value_generic = self._conf["generic"]
        default_value_chart = self._conf["generic"]["chart"]
        default_values = {"chart": default_value_chart}
        for survey in Survey.objects.all():
            if self._conf.get(survey.name) is None:
                self._conf[survey.name] = default_value_generic
            categories = {}
            for category in survey.categories.all():
                categories[category.name] = default_values
            self._conf[survey.name]["categories"] = categories
            questions = {}
            for question in survey.questions.all():
                questions[question.text] = default_values
            self._conf[survey.name]["questions"] = questions
