# -*- coding: utf-8 -*-

import logging
import uuid

from django import forms
from django.conf import settings
from django.forms import models
from django.urls import reverse
from django.utils.text import slugify

from survey.models import Answer, Question, Response
from survey.signals import survey_completed
from survey.widgets import ImageSelectWidget

LOGGER = logging.getLogger(__name__)


class ResponseForm(models.ModelForm):

    FIELDS = {
        Question.TEXT: forms.CharField,
        Question.SHORT_TEXT: forms.CharField,
        Question.SELECT_MULTIPLE: forms.MultipleChoiceField,
        Question.INTEGER: forms.IntegerField,
        Question.FLOAT: forms.FloatField,
    }

    WIDGETS = {
        Question.TEXT: forms.Textarea,
        Question.SHORT_TEXT: forms.TextInput,
        Question.RADIO: forms.RadioSelect,
        Question.SELECT: forms.Select,
        Question.SELECT_IMAGE: ImageSelectWidget,
        Question.SELECT_MULTIPLE: forms.CheckboxSelectMultiple,
    }

    class Meta:
        model = Response
        fields = ()

    def __init__(self, *args, **kwargs):
        """ Expects a survey object to be passed in initially """
        self.survey = kwargs.pop("survey")
        self.user = kwargs.pop("user")
        try:
            self.step = int(kwargs.pop("step"))
        except KeyError:
            self.step = None
        super(ResponseForm, self).__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex
        self.steps_count = len(self.survey.questions.all())
        # will contain prefetched data to avoid multiple db calls
        self.response = False
        self.answers = False

        # add a field for each survey question, corresponding to the question
        # type as appropriate.
        data = kwargs.get("data")
        for i, question in enumerate(self.survey.questions.all()):
            is_current_step = i != self.step and self.step is not None
            if self.survey.display_by_question and is_current_step:
                continue
            self.add_question(question, data)

        self._get_preexisting_response()

        if not self.survey.editable_answers and self.response is not None:
            for name in self.fields.keys():
                self.fields[name].widget.attrs["disabled"] = True

    def _get_preexisting_response(self):
        """ Recover a pre-existing response in database.

        The user must be logged. Will store the response retrieved in an attribute
        to avoid multiple db calls.

        :rtype: Response or None"""
        if self.response:
            return self.response

        if not self.user.is_authenticated:
            self.response = None
        else:
            try:
                self.response = Response.objects.prefetch_related("user", "survey").get(
                    user=self.user, survey=self.survey
                )
            except Response.DoesNotExist:
                LOGGER.debug("No saved response for '%s' for user %s", self.survey, self.user)
                self.response = None
        return self.response

    def _get_preexisting_answers(self):
        """ Recover pre-existing answers in database.

        The user must be logged. A Response containing the Answer must exists.
        Will create an attribute containing the answers retrieved to avoid multiple
        db calls.

        :rtype: dict of Answer or None"""
        if self.answers:
            return self.answers

        response = self._get_preexisting_response()
        if response is None:
            self.answers = None
        try:
            answers = Answer.objects.filter(response=response).prefetch_related("question")
            self.answers = {answer.question.id: answer for answer in answers.all()}
        except Answer.DoesNotExist:
            self.answers = None

        return self.answers

    def _get_preexisting_answer(self, question):
        """ Recover a pre-existing answer in database.

        The user must be logged. A Response containing the Answer must exists.

        :param Question question: The question we want to recover in the
        response.
        :rtype: Answer or None"""
        answers = self._get_preexisting_answers()
        return answers.get(question.id, None)

    def get_question_initial(self, question, data):
        """ Get the initial value that we should use in the Form

        :param Question question: The question
        :param dict data: Value from a POST request.
        :rtype: String or None  """
        initial = None
        answer = self._get_preexisting_answer(question)
        if answer:
            # Initialize the field with values from the database if any
            if question.type == Question.SELECT_MULTIPLE:
                initial = []
                if answer.body == "[]":
                    pass
                elif "[" in answer.body and "]" in answer.body:
                    initial = []
                    unformated_choices = answer.body[1:-1].strip()
                    for unformated_choice in unformated_choices.split(settings.CHOICES_SEPARATOR):
                        choice = unformated_choice.split("'")[1]
                        initial.append(slugify(choice))
                else:
                    # Only one element
                    initial.append(slugify(answer.body))
            else:
                initial = answer.body
        if data:
            # Initialize the field field from a POST request, if any.
            # Replace values from the database
            initial = data.get("question_%d" % question.pk)
        return initial

    def get_question_widget(self, question):
        """ Return the widget we should use for a question.

        :param Question question: The question
        :rtype: django.forms.widget or None """
        try:
            return self.WIDGETS[question.type]
        except KeyError:
            return None

    @staticmethod
    def get_question_choices(question):
        """ Return the choices we should use for a question.

        :param Question question: The question
        :rtype: List of String or None """
        qchoices = None
        if question.type not in [Question.TEXT, Question.SHORT_TEXT, Question.INTEGER, Question.FLOAT]:
            qchoices = question.get_choices()
            # add an empty option at the top so that the user has to explicitly
            # select one of the options
            if question.type in [Question.SELECT, Question.SELECT_IMAGE]:
                qchoices = tuple([("", "-------------")]) + qchoices
        return qchoices

    def get_question_field(self, question, **kwargs):
        """ Return the field we should use in our form.

        :param Question question: The question
        :param **kwargs: A dict of parameter properly initialized in
            add_question.
        :rtype: django.forms.fields """
        # logging.debug("Args passed to field %s", kwargs)
        try:
            return self.FIELDS[question.type](**kwargs)
        except KeyError:
            return forms.ChoiceField(**kwargs)

    def add_question(self, question, data):
        """ Add a question to the form.

        :param Question question: The question to add.
        :param dict data: The pre-existing values from a post request. """
        kwargs = {"label": question.text, "required": question.required}
        initial = self.get_question_initial(question, data)
        if initial:
            kwargs["initial"] = initial
        choices = self.get_question_choices(question)
        if choices:
            kwargs["choices"] = choices
        widget = self.get_question_widget(question)
        if widget:
            kwargs["widget"] = widget
        field = self.get_question_field(question, **kwargs)
        if question.category:
            field.widget.attrs["category"] = question.category.name
        else:
            field.widget.attrs["category"] = ""
        # logging.debug("Field for %s : %s", question, field.__dict__)
        self.fields["question_%d" % question.pk] = field

    def has_next_step(self):
        if self.survey.display_by_question:
            if self.step < self.steps_count - 1:
                return True
        return False

    def next_step_url(self):
        if self.has_next_step():
            context = {"id": self.survey.id, "step": self.step + 1}
            return reverse("survey-detail-step", kwargs=context)

    def current_step_url(self):
        return reverse("survey-detail-step", kwargs={"id": self.survey.id, "step": self.step})

    def save(self, commit=True):
        """ Save the response object """
        # Recover an existing response from the database if any
        #  There is only one response by logged user.
        response = self._get_preexisting_response()
        if not self.survey.editable_answers and response is not None:
            return None
        if response is None:
            response = super(ResponseForm, self).save(commit=False)
        response.survey = self.survey
        response.interview_uuid = self.uuid
        if self.user.is_authenticated:
            response.user = self.user
        response.save()
        # response "raw" data as dict (for signal)
        data = {"survey_id": response.survey.id, "interview_uuid": response.interview_uuid, "responses": []}
        # create an answer object for each question and associate it with this
        # response.
        for field_name, field_value in list(self.cleaned_data.items()):
            if field_name.startswith("question_"):
                # warning: this way of extracting the id is very fragile and
                # entirely dependent on the way the question_id is encoded in
                # the field name in the __init__ method of this form class.
                q_id = int(field_name.split("_")[1])
                question = Question.objects.get(pk=q_id)
                answer = self._get_preexisting_answer(question)
                if answer is None:
                    answer = Answer(question=question)
                if question.type == Question.SELECT_IMAGE:
                    value, img_src = field_value.split(":", 1)
                    # TODO Handling of SELECT IMAGE
                    LOGGER.debug("Question.SELECT_IMAGE not implemented, please use : %s and %s", value, img_src)
                answer.body = field_value
                data["responses"].append((answer.question.id, answer.body))
                LOGGER.debug("Creating answer for question %d of type %s : %s", q_id, answer.question.type, field_value)
                answer.response = response
                answer.save()
        survey_completed.send(sender=Response, instance=response, data=data)
        return response
