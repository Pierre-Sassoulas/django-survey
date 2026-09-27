# Generating a pdf report from the survey's result

There is a default configuration for PDF generation, but you might want to change
`TEX_CONFIGURATION_FILE` for better results (in particular for language other than
english).

You can manage the way the report is created in a yaml file, globally, survey by survey,
or question by question. In order to render pdf you will need to install `xelatex`. You
will also need python3-tk for sankey's diagram.

The results are generated for the server only when needed, but you can force it as a
developer with:

```bash
python manage.py exportresult -h
```

Following is an example of a configuration file. you can generate one with:

```bash
python manage.py generatetexconf -h
```

## Basic example

```yaml
generic:
  document_option: 11pt
"Test survëy":
  document_class: report
  questions:
    "Lorem ipsum dolor sit amët, <strong> consectetur </strong> adipiscing elit.":
      chart:
        type: polar
        text: pin
    "Dolor sit amët, consectetur<strong>  adipiscing</strong>  elit.":
      chart:
        type: cloud
        text: inside
```

The pdf is then generated using the very good pgf-pie library.

![The generated pdf for the polar and pin options](report.png "The generated pdf for the polar and pin options")

![The generated pdf for the cloud and inside options](report_2.png "The generated pdf for the cloud and inside options")

## Sankey diagram

If you installed python3-tk, you can also show the relation between two questions using
a sankey diagram :

```yaml
"Lorem ipsum dolor sit amët, <strong> consectetur </strong> adipiscing elit.":
  chart:
    type: sankey
    question: "Dolor sit amët, consectetur<strong>  adipiscing</strong>  elit."
```

You get this as a result:

![The generated pdf for the sankey example](sankey.png "The generated pdf for the sankey example")

## Advanced example

You can also limit the answers shown by cardinality, filter them, group them together
and choose the color for each answer or group of answers.

If you use this configuration for the previous question:

```yaml
"Test survëy":
  "Dolor sit amët, consectetur<strong>  adipiscing</strong>  elit.":
    multiple_charts:
      "Sub Sub Section with radius=3":
        color:
          Yës: blue!50
          No: red!50
          Whatever: red!50!blue!50
        radius: 3
      "Sub Sub Section with text=pin":
        group_together:
          Nah:
            - No
            - Whatever
          K.:
            - Yës
        color:
          Nah: blue!33!red!66
          K.: blue!50
        text: pin
    chart:
      radius: 1
      type: cloud
      text: inside
```

You get this as a result:

![The generated pdf for the multiple charts example](multicharts.png "The generated pdf for the multiple charts example")

## Implementing a custom treatment

If you want to make your own treatment you can use your own class, for example.

Configuration:

```yaml
"Test survëy":
  questions:
    "Ipsum dolor sit amët, <strong> consectetur </strong>  adipiscing elit.":
      chart:
        type: survey.tests.exporter.tex.CustomQuestion2TexChild
```

Code in `survey.tests.exporter.tex.CustomQuestion2TexChild`:

```python
from survey.exporter.tex.question2tex_chart import Question2TexChart


class CustomQuestion2TexChild(Question2TexChart):
    def get_results(self):
        self.type = "polar"
        return """        2/There were no answer at all,
        3/But we have a custom treatment to show some,
        2/You can make minor changes too !"""
```

Result:

![The generated pdf for the custom example](custom.png "The generated pdf for the custom example")

For a full example of a configuration file look at
{download}`example_conf.yaml <example_conf.yaml>`, you can also generate your
configuration file with `python manage.py generatetexconf -h`, it will create the
default skeleton for every survey and question.

To guide you during the python development, you can read:

- The default reporter for PieChart in `Question2TexChart` :
  https://github.com/Pierre-Sassoulas/django-survey/blob/main/survey/exporter/tex/question2tex_chart.py#L13
- The Sankey reporter in `Question3TexSankey` :
  https://github.com/Pierre-Sassoulas/django-survey/blob/main/survey/exporter/tex/question2tex_sankey.py#L15
- The Raw reporter in `Question2TexRax` :
  https://github.com/Pierre-Sassoulas/django-survey/blob/main/survey/exporter/tex/question2tex_raw.py

Do not hesitate to make a pull request with your new exporter if it can be of interest
for others I'll integrate it.
