import logging

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from survey.models import Question

LOGGER = logging.getLogger(__name__)


class Question2Tex:

    """
    This class permit to generate latex code directly from the Question
    object after overriding the tex() function.
    """

    TEX_SKELETON = ""

    def __init__(self, question, **options):
        self.question = question
        self.min_cardinality = options.get("min_cardinality", 0)
        self.group_by_letter_case = options.get("group_by_letter_case")
        self.group_by_slugify = options.get("group_by_slugify")
        self.group_together = options.get("group_together")
        self.sort_answer = options.get("sort_answer")
        self.filter = options.get("filter")
        self.cardinality = self.question.sorted_answers_cardinality(
            self.min_cardinality,
            self.group_together,
            self.group_by_letter_case,
            self.group_by_slugify,
            self.filter,
            self.sort_answer,
        )

    @staticmethod
    def html2latex(html_text):
        """Convert some html text to something latex can compile.

        About the implementation : I added only what I used in my own questions
        here, because html2latex (https://pypi.python.org/pypi/html2latex/) is
        adding more than 12 Mo to the virtualenv size and 8 dependencies !
            (Jinja (378kB), Pillow (7.5MB), lxml (3.5MB), pyenchant (60kB),
             redis (62kB), selenium (2.6MB), ipython (2.8MB) nose (154kB)

        :param String html_text: Some html text."""
        html_text = html_text.replace("<strong>", "\\textbf{")
        html_text = html_text.replace("</strong>", "}")
        html_text = html_text.replace("<code>", "$")
        html_text = html_text.replace("</code>", "$")
        html_text = html_text.replace("&lt;", "<")
        html_text = html_text.replace("&gt;", ">")
        return html_text

    def get_caption_min_cardinality(self):
        """A descriptive text for the min_cardinality option."""
        caption = ""
        if self.min_cardinality > 0:
            caption += "{} {} ".format(
                _("with"),
                ngettext(
                    "%(min_cardinality)d respondents or more",
                    "%(min_cardinality)d respondent or more",
                    self.min_cardinality,
                )
                % {"min_cardinality": self.min_cardinality},
            )
        return caption

    def get_caption_filter(self):
        """A descriptive text for the filter option."""
        caption = ""
        if self.filter:
            caption += "{} ".format(_("excluding"))
            for i, excluded in enumerate(self.filter):
                excluded = Question2Tex.get_clean_answer(excluded)
                caption += f"'{excluded}', "
                if len(self.filter) >= 2 and i == len(self.filter) - 2:
                    caption += "{} ".format(_("and"))
            caption = f"{caption[:-2]} "
        return caption

    def get_caption_group_together(self):
        """A descriptive text for the group_together option."""
        caption = ""
        if self.group_together:
            if self.cardinality is None:
                loop_dict = self.group_together
            else:
                # Looping only on the value really used in the answers
                loop_dict = self.cardinality
            has_and = False
            for key in loop_dict:
                values = self.group_together.get(key)
                if values is None:
                    # group_together does not contain every answers
                    continue
                standardized_values = Question.standardize_list(
                    values, self.group_by_letter_case, self.group_by_slugify
                )
                standardized_key = Question.standardize(key, self.group_by_letter_case, self.group_by_slugify)
                relevant_values = [v for v in standardized_values if v != standardized_key]
                if not relevant_values:
                    # If there is no relevant value the group_together was just
                    # a placeholder ex Yes for [yes Yës yEs]
                    continue
                # We duplicate the translations so makemessage find it
                caption += f"with '{key}' standing for "
                for value in values:
                    caption += "'{}' {} ".format(value, _("or"))
                caption = caption[: -len("{} ".format(_("or")))]
                has_and = True
                caption += "{} ".format(_("and"))
            if has_and:
                # We remove the final "and " if there is one
                caption = caption[: -len("{} ".format(_("and")))]
        return caption

    def get_caption_specifics(self):
        msg = "Question2Tex.get_caption_specifics() is abstract."
        raise NotImplementedError(msg)

    def get_caption(self):
        """Return a caption with an appropriate description of the figure."""
        caption = "{} ".format(_("Repartition of answers"))
        caption += self.get_caption_min_cardinality()
        caption += self.get_caption_filter()
        caption += self.get_caption_specifics()
        caption += self.get_caption_group_together()
        # We remove the last trailing space
        return f"{caption[:-1]}."

    @staticmethod
    def get_clean_answer(answer):
        if not answer or answer == "[]":
            answer = _(settings.USER_DID_NOT_ANSWER)
        else:
            replace_list = [",", "\n", "\r", "/", " "]
            for char in replace_list:
                answer = answer.replace(char, " ")
        return answer

    def tex(self):
        raise NotImplementedError("Question2Tex.tex() is abstract.")
