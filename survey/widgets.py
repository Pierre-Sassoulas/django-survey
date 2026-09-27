from django import forms


class ImageSelectWidget(forms.widgets.Widget):
    template_name = "survey/forms/image_select.html"

    class Media:
        js = ("survey/js/survey.js",)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        image_choices = []
        for index, (full_value, label) in enumerate(self.choices):
            if full_value != "":
                # Choices are written as 'value:image_url', but the key is slugified
                choice_value, img_src = label.split(":", 1)
                image_choices.append(
                    {"img_src": img_src, "value": choice_value, "full_value": full_value, "index": index}
                )
        context["widget"]["image_choices"] = image_choices
        return context
