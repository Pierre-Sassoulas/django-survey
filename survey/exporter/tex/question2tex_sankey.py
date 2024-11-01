import logging
import warnings

from django.utils.translation import gettext_lazy as _

try:
    from pandas.core.frame import DataFrame
    from pysankey import sankey

    SANKEY = True
except ModuleNotFoundError as e:
    warnings.warn(
        "Cannot import 'sankey', please install the package using"
        "the sankey extra. (pip install django-survey-and-report[sankey])"
        f": '{e}'",
        stacklevel=2,
    )
    SANKEY = False

from survey.exporter.tex.question2tex import Question2Tex
from survey.models.question import Question

LOGGER = logging.getLogger(__name__)


class SankeyNotInstalled(Exception):
    def __init__(self):
        super().__init__(_("Cannot generate PDF, we need 'pySankeyBeta' to be installed."))


class Question2TexSankey(Question2Tex):
    """
    This class permit to generate latex code directly from the Question
    object.
    """

    TEX_SKELETON = """
\\begin{figure}[h!]
    \\includegraphics[width=\\textwidth]{%s}
    \\caption{\\label{figure:q%dvsq%d}%s}
\\end{figure}
"""

    def __init__(self, question, **options):
        other_question = options.get("other_question")
        if not isinstance(other_question, Question):
            msg = f"Expected a 'Question' and got '{other_question}'"
            msg += f" (a '{other_question.__class__.__name__}')."
            raise TypeError(msg)
        del options["other_question"]
        super().__init__(question, **options)
        self.other_question = other_question

    def get_caption_specifics(self):
        caption = "{} '{}' ({}) ".format(_("for the question"), Question2Tex.html2latex(self.question.text), _("left"))
        caption += "{} '{}' ({}) ".format(
            _("in relation with the question"),
            Question2Tex.html2latex(self.other_question.text),
            _("right"),
        )
        return caption

    def tex(self):
        """Return a tikz Sankey Diagram of two questions.

        The question used during initialization will be left and down the other
        question will be right and up. Cardinality constraint used for the
        other question are the same for both question.

        See this question https://tex.stackexchange.com/questions/40159/
        in order for it to work with your latex file.

        :param Question other_question: the question we compare to."""
        if not SANKEY:
            raise SankeyNotInstalled()
        self.cardinality = self.question.sorted_answers_cardinality(
            self.min_cardinality,
            self.group_together,
            self.group_by_letter_case,
            self.group_by_slugify,
            self.filter,
            self.sort_answer,
            other_question=self.other_question,
        )
        q1 = []
        q2 = []
        for answer_to_q1, cardinality_to_q2 in list(self.cardinality.items()):
            for answer_to_q2, number_of_time in list(cardinality_to_q2.items()):
                q1 += [answer_to_q1] * number_of_time
                q2 += [answer_to_q2] * number_of_time
        df = DataFrame(data={self.question.text: q1, self.other_question.text: q2})
        name = f"tex/q{self.question.pk}_vs_q{self.other_question.pk}"
        sankey(df[self.question.text], df[self.other_question.text], aspect=20, fontsize=10, figureName=name)
        return Question2TexSankey.TEX_SKELETON % (
            name[4:],
            self.question.pk,
            self.other_question.pk,
            self.get_caption(),
        )
