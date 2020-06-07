from django.db import migrations, models

from survey.models import Survey


def convert_bool_to_small_int(apps, _schema_editor):
    oldSurvey = apps.get_model("survey", "Survey")
    for survey in oldSurvey.objects.all():
        survey.display_method = Survey.BY_QUESTION if survey.display_by_question else Survey.ALL_IN_ONE_PAGE
        survey.save()


class Migration(migrations.Migration):

    dependencies = [("survey", "0011_survey_publish_duration")]

    operations = [
        migrations.AddField(
            model_name="survey",
            name="display_method",
            field=models.SmallIntegerField(
                choices=[(1, "By question"), (2, "By category"), (0, "All in one page")],
                default=0,
                verbose_name="Display method",
            ),
        ),
        migrations.RunPython(convert_bool_to_small_int),
        migrations.RemoveField(model_name="survey", name="display_by_question"),
    ]
