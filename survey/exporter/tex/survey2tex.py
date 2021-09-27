import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from pydoc import locate
from shutil import copy, which

import pytz
from django.contrib.messages import ERROR
from django.http import HttpResponse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from survey.exporter.survey2x import Survey2X
from survey.exporter.tex.configuration import Configuration
from survey.exporter.tex.latex_file import LatexFile
from survey.exporter.tex.question2tex import Question2Tex
from survey.exporter.tex.question2tex_chart import Question2TexChart
from survey.exporter.tex.question2tex_raw import Question2TexRaw
from survey.exporter.tex.question2tex_sankey import SANKEY, Question2TexSankey, SankeyNotInstalled
from survey.models.question import Question

LOGGER = logging.getLogger(__name__)
STATIC = Path(__file__).parent.parent.parent.joinpath("static")


class XelatexNotInstalled(Exception):
    def __init__(self):
        super().__init__(_("Cannot generate PDF, we need 'xelatex' to be installed."))


class Survey2Tex(Survey2X):

    ANALYSIS_FUNCTION = []
    PGF_PIE_STY = Path(STATIC, "survey", "sty", "pgf-pie.sty")
    PGF_PLOT_STY = Path(STATIC, "survey", "sty", "pgfplots.sty")

    def __init__(self, survey, configuration=None):
        super().__init__(survey)
        if configuration is None:
            configuration = Configuration()
        self.tconf = configuration

    def _additional_analysis(self, survey, latex_file):
        """Perform additional analysis."""
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
                question_synthesis += f"\\{mct}{{{chart_title}}}"
            tex_type = opts.get("type")
            if tex_type == "raw":
                question_synthesis += Question2TexRaw(question, **opts).tex()
            elif tex_type == "sankey":
                if not SANKEY:
                    raise SankeyNotInstalled()
                other_question_text = opts["question"]
                other_question = Question.objects.get(text=other_question_text)
                q2tex = Question2TexSankey(question, other_question=other_question)
                question_synthesis += q2tex.tex()
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
\\clearpage{{}}
\\section{{{}}}

\\label{{sec:{}}}

{}

""".format(
            section_title,
            question.pk,
            question_synthesis,
        )

    @property
    def file_modification_time(self):
        """Return the modification time of the pdf."""
        if not self.pdf_filename.exists():
            earliest_working_timestamp_for_windows = 86400
            mtime = earliest_working_timestamp_for_windows
        else:
            mtime = os.path.getmtime(self.pdf_filename)
        mtime = datetime.utcfromtimestamp(mtime)
        mtime = mtime.replace(tzinfo=pytz.timezone("UTC"))
        return mtime

    def __generation_done_once(self):
        return os.path.exists(self.pdf_filename)

    def __str__(self):
        return self.create_tex()

    @property
    def pdf_filename(self) -> Path:
        return Path(self.directory, "{}.{}".format(slugify(self.survey.name), "pdf"))

    def generate_pdf(self):
        """Compile the pdf from the tex file. Can raise subprocess.CalledProcessError"""
        if not self.need_update():
            LOGGER.info("<%s> is already generated and up to date.", self.pdf_filename)
            return
        LOGGER.debug("Generating <%s>", self.filename)
        self.generate_file()
        LOGGER.debug("Generated <%s>. Now compilating with xelatex to get <%s>.", self.filename, self.pdf_filename)
        self.compile_pdf()

    def create_tex(self, questions=None):
        if questions is None:
            questions = self.survey.questions.all()
        document_class = self.tconf.get("document_class", survey_name=self.survey.name)
        kwargs = self.tconf.get(survey_name=self.survey.name)
        del kwargs["document_class"]
        ltxf = LatexFile(document_class, **kwargs)
        for question in questions:
            ltxf.text += self.treat_question(question)
        self._additional_analysis(self.survey, ltxf)
        if not ltxf.text:
            ltxf.text = _("No questions to display in this survey.")
        return ltxf.document

    def compile_pdf(self):
        """Compile the pdf from the tex file."""
        xelatex = "xelatex"
        if which(xelatex) is None:
            raise XelatexNotInstalled()
        previous_directory = os.getcwd()
        LOGGER.debug("Generating the pdf corresponding to <%s>", self.filename)
        os.chdir(self.filename.parent)
        sty_dependencies = [self.PGF_PIE_STY, self.PGF_PLOT_STY]
        dependencies_to_delete = []
        for sty_dependency in sty_dependencies:
            dependencies_to_delete.append(Path(self.filename.parent, sty_dependency.name))
            LOGGER.debug("Copying <%s> temporarily to <%s>", sty_dependency, self.filename.parent)
            copy(sty_dependency, self.filename.parent)
        xelatex_command = [xelatex, "-interaction=batchmode", "-halt-on-error", self.filename.name]
        LOGGER.debug("Launching first compilation with <%s>.", xelatex_command)
        result = subprocess.check_output(xelatex_command)
        LOGGER.debug("First compilation had the following output: %s", result)
        LOGGER.debug("Launching second compilation for ref/label and proper table of content.")
        subprocess.check_output(xelatex_command)
        for sty_dependency in dependencies_to_delete:
            sty_dependency.unlink()
        os.chdir(previous_directory)

    @staticmethod
    def export_as_tex(modeladmin, request, queryset):
        if len(queryset) != 1:
            modeladmin.message_user(request, _("Cannot export multiple PDF, choose only one."), level=ERROR)
            return
        survey = queryset.first()
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename={survey.safe_name}.pdf"
        s2tex = Survey2Tex(survey=survey)
        try:
            s2tex.generate_pdf()
        except subprocess.CalledProcessError as exc:
            modeladmin.message_user(request, _("Error during PDF generation: %s" % exc), level=ERROR)
            return
        with open(s2tex.pdf_filename, "rb") as f:
            response.write(f.read())
        return response


Survey2Tex.export_as_tex.short_description = _("Export to PDF")
