from crispy_forms.layout import TEMPLATE_PACK, LayoutObject
from django.template.loader import render_to_string


class Formset(LayoutObject):
    """
    Layout object. It renders an entire formset, as though it were a Field.

    Example:

    Formset("attached_files_formset")
    """

    template = "vocabs/formset.html"

    def __init__(self, formset_name_in_context, template=None):
        self.formset_name_in_context = formset_name_in_context

        # crispy_forms/layout.py:302 requires us to have a fields property
        self.fields = []

        # Overrides class variable with an instance level variable
        if template:
            self.template = template

    def render(self, form, context, template_pack=TEMPLATE_PACK, **kwargs):
        formset = context[self.formset_name_in_context]

        # Handle different context types (dict vs Context object)
        template_context = {"formset": formset}

        # Extract request from context if available for Django 5.x compatibility
        request = None
        if hasattr(context, "get"):
            request = context.get("request")
        elif hasattr(context, "request"):
            request = context.request

        return render_to_string(self.template, template_context, request=request)
