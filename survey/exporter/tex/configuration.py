# -*- coding: utf-8 -*-

import copy
import logging
import os

import yaml
from django.conf import settings

from survey.models.survey import Survey

LOGGER = logging.getLogger(__name__)


class Configuration(object):

    DEFAULT_PATH = os.path.join(
        settings.ROOT, "survey", "exporter", "tex", "default_conf.yaml"
    )

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
        return yaml.safe_dump(
            self._conf, default_flow_style=False, encoding=None, allow_unicode=True
        )

    @property
    def valid_survey_names(self):
        """ Return a list of the valid name for a survey. """
        valid_survey_names = [survey.name for survey in Survey.objects.all()]
        valid_survey_names.append("generic")
        return valid_survey_names

    def check_survey_exists(self, survey_name):
        """ Check if the survey name exists.

        :param String survey_name: The name of a survey. """
        LOGGER.info("Checking that '%s' is an existing survey.", survey_name)
        if type(survey_name) == Survey:
            msg = "Expecting a string for 'survey_name' and got a Survey "
            msg += " ('{}').".format(survey_name)
            raise TypeError(msg)
        if survey_name not in self.valid_survey_names:
            msg = "'{}' is not an existing survey in the ".format(survey_name)
            msg += "database.\nPossible values are :\n"
            for name in self.valid_survey_names:
                msg += "- '{}'\n".format(name)
            # Remove the last "\n"
            msg = msg[:-1]
            LOGGER.warning(msg)

    def __getitem__(self, survey_name):
        return self.get(survey_name=survey_name)

    def _init_from_file(self, filepath):
        """ Return a configuration from a filepath.

        :param String filepath: The path of the yaml configuration file.
        :rtype: Dict """
        with open(filepath, "r", encoding="UTF-8") as f:
            configuration = yaml.save_load(f)
        for survey_name in list(configuration.keys()):
            self.check_survey_exists(survey_name)
            if not configuration[survey_name]:
                raise ValueError("Nothing in %s's configuration" % survey_name)
        return configuration

    def optional_update(self, dict_, update_dict, key):
        """ Update a dict with another one if optional key exists. """
        try:
            self.recursive_update(dict_, update_dict[key])
        except KeyError:
            # There is not configuration file for key, only the default one
            pass

    def recursive_update(self, d, u):
        """ Update a dict recursively. It permit to keep the default value by
        default and to be able to replace them by dictionaries.
        """
        import collections

        # print("d", d, "u", u)
        if d is None:
            return u
        for k, v in list(u.items()):
            # print("k", k, "v", v)
            if isinstance(v, collections.Mapping):
                r = self.recursive_update(d.get(k, {}), v)
                # print("Recursive value for {} :{}".format(k, v))
                d[k] = r
            else:
                d[k] = u[k]
        return d

    def get_multiple_charts(self, d):
        """ Permit to get a dict while the default value is None. """
        multiple_charts = d.get("multiple_charts")
        return {} if multiple_charts is None else multiple_charts

    def update(self, d, u):
        """ Update a dictionary and handle the multiple charts values. """
        self.recursive_update(d, u)
        multiple_charts = self.get_multiple_charts(d)
        for chart, chart_conf in list(multiple_charts.items()):
            chart_conf = copy.deepcopy(d["chart"])
            umc = self.get_multiple_charts(u).get(chart, {})
            self.recursive_update(chart_conf, umc)
            d["multiple_charts"][chart] = chart_conf

    def get_default_question_conf(self, conf):
        """ A deepcopy of what we deem necessary in the question config.

        We want to avoid copying everything in the conf. For example we do not
        need the document type in a question configuration.

        :param dict conf: Full configuration with useless element for questions
        """
        return {
            "chart": copy.deepcopy(conf["chart"]),
            "multiple_charts": copy.deepcopy(conf["multiple_charts"]),
            "multiple_chart_type": copy.deepcopy(conf["multiple_chart_type"]),
        }

    def get(self, key=None, survey_name=None, question_text=None):
        """ Get a configuration file for a survey or a specific question.

        :param String key: The key we want to get.
        :param String survey_name: The name of a specific survey.
        :param String question_text: The text of a specific question.
        :param String category_name """
        # We create a new dictionary from a deepcopy of the default conf
        conf = copy.deepcopy(self._default["generic"])
        # We update it with the generic configuration of the user if it exists
        self.optional_update(conf, self._conf, "generic")
        if survey_name:
            self.check_survey_exists(survey_name)
            if type(survey_name) is Survey:
                # If a dev gave a Survey object we do not bother him with type
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
            msg = ""
            if survey_name:
                msg += "for survey '{}', ".format(survey_name)
            if question_text:
                msg += "and question '{}', ".format(question_text)
            msg += "key '{}' does not exists. ".format(key)
            msg += "Possible values : {}".format(list(conf.keys()))
            LOGGER.error(msg)
            raise ValueError(msg)
