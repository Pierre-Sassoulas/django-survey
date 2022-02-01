import copy
import logging
from collections.abc import Mapping
from pathlib import Path

import yaml

from survey.models.survey import Survey

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).parent


class Configuration:

    DEFAULT_PATH = Path(HERE, "default_conf.yaml")

    def __init__(self, configuration_file=None):
        self._default = self._init_from_file(self.DEFAULT_PATH)
        if configuration_file is not None:
            self._conf = self._init_from_file(configuration_file)
        else:
            self._conf = {}

    def __str__(self, *args, **kwargs):
        # Default flow style prevent
        # b:
        #   c: 3
        #   d: 4
        # To become the ugly :
        # b: {c: 3, d: 4}
        return yaml.safe_dump(self._conf, default_flow_style=False, encoding=None, allow_unicode=True)

    @property
    def valid_survey_names(self):
        """Return a list of the valid name for a survey."""
        valid_survey_names = [survey.name for survey in Survey.objects.all()]
        valid_survey_names.append("generic")
        return valid_survey_names

    def check_survey_exists(self, survey_name):
        """Check if the survey name exists.

        :param String survey_name: The name of a survey."""
        LOGGER.info("Checking that '%s' is an existing survey.", survey_name)
        if not isinstance(survey_name, str):
            msg = f"Expecting a string for 'survey_name' and got a {type(survey_name)} "
            msg += f" ('{survey_name}')."
            raise TypeError(msg)
        if survey_name not in self.valid_survey_names:
            msg = f"'{survey_name}' is not an existing survey in the "
            msg += "database.\nPossible values are :\n"
            for name in self.valid_survey_names:
                msg += f"- '{name}'\n"
            # Remove the last "\n"
            msg = msg[:-1]
            LOGGER.warning(msg)

    def __getitem__(self, survey_name):
        return self.get(survey_name=survey_name)

    def _init_from_file(self, filepath):
        """Return a configuration from a filepath.

        :param String filepath: The path of the yaml configuration file.
        :rtype: Dict"""
        with open(filepath, encoding="UTF-8") as f:
            configuration = yaml.load(f, Loader=yaml.FullLoader)
        for survey_name in list(configuration.keys()):
            self.check_survey_exists(survey_name)
            if not configuration[survey_name]:
                raise ValueError("Nothing in %s's configuration" % survey_name)
        return configuration

    def optional_update(self, dict_, update_dict, key):
        """Update a dict with another one if optional key exists."""
        try:
            self.recursive_update(dict_, update_dict[key])
        except KeyError:
            # There is no configuration file for key, only the default one
            pass

    def recursive_update(self, dict_, update_dict):
        """Update a dict recursively. It permits to keep the default value by
        default and to be able to replace them by dictionaries.
        """
        if dict_ is None:
            return update_dict
        for key, value in update_dict.items():
            if isinstance(value, Mapping):
                result = self.recursive_update(dict_.get(key, {}), value)
                dict_[key] = result
            else:
                dict_[key] = update_dict[key]
        return dict_

    @staticmethod
    def get_multiple_charts(dict_):
        """Permit to get a dict while the default value is None."""
        multiple_charts = dict_.get("multiple_charts")
        return {} if multiple_charts is None else multiple_charts

    def update(self, dict_, update):
        """Update a dictionary and handle the multiple charts values."""
        self.recursive_update(dict_, update)
        multiple_charts = self.get_multiple_charts(dict_)
        for chart, chart_conf in list(multiple_charts.items()):
            chart_conf = copy.deepcopy(dict_["chart"])
            umc = self.get_multiple_charts(update).get(chart, {})
            self.recursive_update(chart_conf, umc)
            dict_["multiple_charts"][chart] = chart_conf

    @staticmethod
    def get_default_question_conf(conf):
        """A deepcopy of what we deem necessary in the question config.

        We want to avoid copying everything in the conf. For example, we do not
        need the document type in a question configuration.

        :param dict conf: Full configuration with useless element for questions
        """
        return {
            "chart": copy.deepcopy(conf["chart"]),
            "multiple_charts": copy.deepcopy(conf["multiple_charts"]),
            "multiple_chart_type": copy.deepcopy(conf["multiple_chart_type"]),
        }

    def get(self, key=None, survey_name=None, question_text=None):
        """Get a configuration file for a survey or a specific question.

        :param String key: The key we want to get.
        :param String survey_name: The name of a specific survey.
        :param String question_text: The text of a specific question."""
        # We create a new dictionary from a deepcopy of the default conf
        conf = copy.deepcopy(self._default["generic"])
        # We update it with the generic configuration of the user if it exists
        self.optional_update(conf, self._conf, "generic")
        if survey_name:
            self.check_survey_exists(survey_name)
            if isinstance(survey_name, Survey):
                # If a dev gave a Survey object we do not bother him with type
                # TODO document this with type annotation
                survey_name = survey_name.name
            # We update the generic configuration with the survey configuration
            self.update(conf, self._conf.get(survey_name, {}))
        for question in conf.get("questions", []):
            # We deepcopy the configuration and update it with question
            # specific configuration, then we copy it in the general conf
            qdc = self.get_default_question_conf(conf)
            self.update(qdc, conf["questions"][question])
            conf["questions"][question] = qdc
        if question_text:
            if conf.get("questions") and conf["questions"].get(question_text):
                conf = conf["questions"][question_text]
            else:
                conf = self.get_default_question_conf(conf)
        if key is None:
            return conf
        try:
            return conf[key]
        except KeyError:
            self.__raise_get_error(conf, key, question_text, survey_name)

    @staticmethod
    def __raise_get_error(conf, key, question_text, survey_name):
        msg = ""
        if survey_name:
            msg += f"for survey '{survey_name}', "
        if question_text:
            msg += f"and question '{question_text}', "
        msg += f"key '{key}' does not exists. "
        msg += f"Possible values : {list(conf.keys())}"
        LOGGER.error(msg)
        raise ValueError(msg)
