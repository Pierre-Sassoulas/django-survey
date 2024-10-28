import logging

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from survey.exporter.tex.question2tex import Question2Tex

LOGGER = logging.getLogger(__name__)


class Question2TexChart(Question2Tex):
    """
    This class permit to generate latex code directly from the Question
    object.
    """

    TEX_SKELETON = """
\\begin{figure}[h!]
    \\begin{tikzpicture}
        \\pie%s{
%s
        }
    \\end{tikzpicture}
    \\caption{\\label{figure:q%d-%d}%s}
\\end{figure}
"""

    def __init__(self, question, **options):
        super().__init__(question, **options)
        self.pos = options.get("pos")
        self.rotate = options.get("rotate")
        self.radius = options.get("radius")
        self.color = options.get("color")
        self.explode = options.get("explode")
        self.sum = options.get("sum")
        self.after_number = options.get("after_number")
        self.before_number = options.get("before_number")
        self.scale_font = options.get("scale_font")
        self.text = options.get("text")
        self.style = options.get("style")
        self.type = options.get("type")
        # This permit to label correctly multiple charts so we do not have the
        # same label for each chart
        self.latex_label = options.get("latex_label", 1)

    def get_colors(self):
        """Return a formatted string for a tikz pgf-pie chart."""
        colors = []
        for answer in self.cardinality:
            answer = Question2Tex.get_clean_answer(answer)
            try:
                colors.append(self.color[answer])
            except (KeyError, ValueError):
                msg = f"Color for '{answer}' not provided. You could "
                msg += f"add '{answer}: \"red!50\"', in your color config."
                LOGGER.warning(msg)
                colors.append(settings.SURVEY_DEFAULT_PIE_COLOR)
        return "{{{}}}".format(", ".join(colors))

    def get_results(self):
        """Return a formatted string for a tikz pgf-pie chart."""
        pie = ""
        for answer, cardinality in list(self.cardinality.items()):
            if not answer:
                ans = _("Left blank")
            ans = Question2Tex.get_clean_answer(answer)
            pie += f"{cardinality}/{ans},"
        if not pie:
            return ""
        final_answers = []
        for answer in pie.split(","):
            if answer:
                final_answers.append(answer)
        return "            {}".format(",\n            ".join(final_answers))

    def get_pie_options(self):
        r"""Return the options of the pie for: \pie[options]{data}"""
        options = ""
        if self.pos:
            options += f"pos={{{self.pos}}},"
        if self.explode:
            options += f"explode={{{self.explode}}},"
        if self.rotate:
            options += f"rotate={self.rotate},"
        if self.radius:
            options += f"radius={self.radius},"
        if self.color:
            options += f"color={self.get_colors()},"
        if self.sum:
            options += f"sum={self.sum},"
        if self.after_number:
            options += f"after number={self.after_number},"
        if self.before_number:
            options += f"before number={self.before_number},"
        if self.scale_font:
            options += "scale font, "
        if self.text:
            options += f"text={self.text},"
        if self.style:
            options += f"style={self.style},"
        if self.type and self.type != "pie":
            options += f"{self.type},"
        # Removing last ','
        options = options[:-1]
        if options:
            return f"[{options}]"
        return ""

    def get_caption_specifics(self):
        return "{} '{}' ".format(_("for the question"), Question2Tex.html2latex(self.question.text))

    def tex(self):
        """Return a pfg-pie pie chart of a question.

        You must use pgf-pie in your latex file for this to works ::
            \\usepackage{pgf-pie}
        See http://pgf-pie.googlecode.com/ for detail and arguments doc."""
        results = self.get_results()
        if not results:
            return str(_("No answers for this question."))
        return Question2TexChart.TEX_SKELETON % (
            self.get_pie_options(),
            results,
            self.question.pk,
            self.latex_label,
            self.get_caption(),
        )
