from django.contrib import admin
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from survey.actions import make_published
from survey.exporter.csv import Survey2Csv
from survey.exporter.tex import Survey2Tex
from survey.models import Answer, Category, Question, Response, Survey


class QuestionInline(admin.StackedInline):
    model = Question
    ordering = ("order", "category")
    extra = 1

    def get_formset(self, request, survey_obj, *args, **kwargs):
        formset = super().get_formset(request, survey_obj, *args, **kwargs)
        if survey_obj:
            formset.form.base_fields["category"].queryset = survey_obj.categories.all()
        return formset


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_published",
        "page",
        "need_logged_user",
        "template",
        "total_questions_display",
    )
    list_filter = ("is_published", "need_logged_user")
    search_fields = ("name", "description")
    inlines = [CategoryInline, QuestionInline]
    actions = [make_published, Survey2Csv.export_as_csv, Survey2Tex.export_as_tex]

    @admin.display(description="Page")
    def page(self, obj):
        url = obj.get_absolute_url()
        return mark_safe(f"<a target='_blank'  href='{url}'>Page</a>")

    @admin.display(description=_("Total questions"))
    def total_questions_display(self, obj):
        return obj.total_questions


class AnswerBaseInline(admin.StackedInline):
    fields = (
        "is_correct",
        "question",
        "body",
    )
    readonly_fields = ("question", "is_correct")
    extra = 0
    model = Answer

    @admin.display(description=_("Is correct"), boolean=True)
    def is_correct(self, obj):
        return obj.is_correct


class ResponseAdmin(admin.ModelAdmin):
    list_display = (
        "interview_uuid",
        "survey",
        "created",
        "user",
        "correct_answers_display",
    )
    list_filter = ("survey", "created")
    date_hierarchy = "created"
    inlines = [AnswerBaseInline]
    # specifies the order as well as which fields to act on
    readonly_fields = (
        "survey",
        "created",
        "updated",
        "interview_uuid",
        "user",
        "correct_answers_display",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("answers__question")

    @admin.display(description=_("Correct answers"))
    def correct_answers_display(self, obj):
        return f"{obj.correct_answers_count} / {obj.total_answers_count}"


# admin.site.register(Question, QuestionInline)
# admin.site.register(Category, CategoryInline)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)
