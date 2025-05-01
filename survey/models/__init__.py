"""
Permit to import everything from survey.models without knowing the details.
"""

from .answer import Answer
from .category import Category
from .question import Question
from .response import Response
from .survey import Survey

__all__ = ["Answer", "Category", "Category", "Question", "Response", "Survey"]
