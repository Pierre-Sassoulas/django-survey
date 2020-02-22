# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime
from pathlib import Path
from pydoc import locate
from shutil import copy

import pytz
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from survey.exporter.survey2x import Survey2X
from survey.exporter.tex.latex_file import LatexFile
from survey.exporter.tex.question2tex import Question2Tex
from survey.exporter.tex.question2tex_chart import Question2TexChart
from survey.exporter.tex.question2tex_raw import Question2TexRaw
from survey.exporter.tex.question2tex_sankey import Question2TexSankey
from survey.models.question import Question

LOGGER = logging.getLogger(__name__)
STATIC = Path(__file__).parent.parent.parent.joinpath("static")


class Survey2Tex(Survey2X):

    ANALYSIS_FUNCTION = []
    PGF_PIE_STY = Path(STATIC, "survey", "sty", "pgf-pie.sty")
    PGF_PLOT_STY = Path(STATIC, "survey", "sty", "pgfplots.sty")

    def __init__(self, survey, configuration=None):
        Survey2X.__init__(self, survey)
        self.tconf = configuration

    def _synthesis(self, survey):
        """ Return a String of a synthesis of the report. """
        pass

    def _additional_analysis(self, survey, latex_file):
        """ Perform additional analysis. """
        for function_ in self.ANALYSIS_FUNCTION:
            LOGGER.info("Performing additional analysis with %s", function_)
            latex_file.text += function_(survey)

    def treat_question(self, question):
        LOGGER.info("Treating, %s %s", question.pk, question.text)
        options = self.tconf.get(survey_name=self.survey.name, question_text=question.text)
        multiple_charts = options.get("multiple_charts")
        if not multiple_charts:
            multiple_charts = {"": options.get("chart")}
        question_synthesis = ""
        i = 0
        for chart_title, opts in list(multiple_charts.items()):
            i += 1
            if chart_title:
                # "" is False, by default we do not add section or anything
                mct = options["multiple_chart_type"]
                question_synthesis += "\\%s{%s}" % (mct, chart_title)
            tex_type = opts.get("type")
            if tex_type == "raw":
                question_synthesis += Question2TexRaw(question, **opts).tex()
            elif tex_type == "sankey":
                other_question_text = opts["question"]
                other_question = Question.objects.get(text=other_question_text)
                q2tex = Question2TexSankey(question)
                question_synthesis += q2tex.tex(other_question)
            elif tex_type in ["pie", "cloud", "square", "polar"]:
                q2tex = Question2TexChart(question, latex_label=i, **opts)
                question_synthesis += q2tex.tex()
            elif locate(tex_type) is None:
                msg = "{} '{}' {}".format(
                    _("We could not render a chart because the type"),
                    tex_type,
                    _(
                        "is not a standard type nor the path to an "
                        "importable valid Question2Tex child class. "
                        "Choose between 'raw', 'sankey', 'pie', 'cloud', "
                        "'square', 'polar' or 'package.path.MyQuestion2Tex"
                        "CustomClass'"
                    ),
                )
                LOGGER.error(msg)
                question_synthesis += msg
            else:
                q2tex_class = locate(tex_type)
                # The use will probably know what type he should use in his
                # custom class
                opts["type"] = None
                q2tex = q2tex_class(question, latex_label=i, **opts)
                question_synthesis += q2tex.tex()
        section_title = Question2Tex.html2latex(question.text)
        return """
\\clearpage{}
\\section{%s}

\\label{sec:%s}

%s

""" % (
            section_title,
            question.pk,
            question_synthesis,
        )

    def generate(self, path, output=None):
        """ Compile the pdf from the tex file. """
        previous_directory = os.getcwd()
        dir_name, file_name = os.path.split(path)
        os.chdir(dir_name)
        sty_dependencies = [self.PGF_PIE_STY, self.PGF_PLOT_STY]
        dependencies_to_delete = []
        for dep in sty_dependencies:
            copy(dep, dir_name)
            dependencies_to_delete.append(Path(dir_name, dep.name))
        os.system("xelatex {}".format(file_name))
        os.system("xelatex {}".format(file_name))
        if output is not None:
            os.system("mv {}.pdf {}".format(file_name[:-3], output))
        for dep in dependencies_to_delete:
            dep.unlink()
        os.chdir(previous_directory)

    @property
    def file_modification_time(self):
        """ Return the modification time of the pdf. """
        pdf_path = Path(self._get_x_dir(), "{}.pdf".format(slugify(self.survey.name)))
        if not pdf_path.exists():
            earliest_working_timestamp_for_windows = 86400
            mtime = earliest_working_timestamp_for_windows
        else:
            mtime = os.path.getmtime(pdf_path)
        mtime = datetime.utcfromtimestamp(mtime)
        mtime = mtime.replace(tzinfo=pytz.timezone("UTC"))
        return mtime

    def __str__(self):
        return self.create_tex()

    def create_tex(self, questions=None):
        if questions is None:
            questions = self.survey.questions.all()
        document_class = self.tconf.get("document_class", survey_name=self.survey.name)
        kwargs = self.tconf.get(survey_name=self.survey.name)
        del kwargs["document_class"]
        ltxf = LatexFile(document_class, **kwargs)
        self._synthesis(self.survey)
        for question in questions:
            ltxf.text += self.treat_question(question)
        self._additional_analysis(self.survey, ltxf)
        return ltxf.document

    def generate_pdf(self):
        """ Compile the pdf from the tex file. """
        self.generate_file()
        self.generate(self.file_name())
