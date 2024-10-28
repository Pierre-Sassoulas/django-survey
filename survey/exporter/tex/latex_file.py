import logging
from datetime import datetime

LOGGER = logging.getLogger(__name__)


class LatexFile:
    """Permit to handle the content of a LatexFile"""

    def __init__(self, document_class, document_option=None, header=None, intro=None, footer=None, date=None, **kwargs):
        LOGGER.debug(
            "Creating a document skeleton with document_class=%s, document_option=%s", document_class, document_option
        )
        self.document_class = document_class
        self.text = ""
        self.document_option = self.set_value(document_option)
        self._header = self.set_value(header)
        self.intro = self.set_value(intro)
        self._footer = self.set_value(footer)
        if date is None:
            date = datetime.now().strftime("%B %d, %Y")
        self.date = date

    def set_value(self, value):
        """Return the value we need for null text."""
        if value is None:
            return ""
        return value

    @property
    def header(self):
        """Return the header of a .tex file.

        :rtype: String"""
        header = "\\documentclass"
        if self.document_option:
            header += f"[{self.document_option}]"
        header += f"{{{self.document_class}}}\n"
        header += f"\\date{{{self.date}}}\n"
        header += f"{self._header}\n"
        header += "\\begin{document}\n"
        header += f"{self.intro}\n"
        return header

    @property
    def footer(self):
        """Return the footer of a .tex file.

        :rtype: String"""
        end = """
\\end{document}
"""
        if self._footer:
            return self._footer + end
        return end

    def save(self, path):
        """Save the document on disk."""
        with open(path, "wb") as tex_file:
            tex_file.write(self.document.encode("UTF-8"))

    @property
    def document(self):
        """Return the full text of the LatexFile.

        :rtype: String"""
        return f"{self.header}{self.text}{self.footer}"
