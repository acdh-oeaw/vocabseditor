from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from django.template.loader import render_to_string


class Formset(LayoutObject):
    """
    Layout object. It renders an entire formset, as though it were a Field.

    Example:

    Formset("attached_files_formset")
    """

    template = "vocabs/formset.html" % TEMPLATE_PACK

    def __init__(self, formset_name_in_context, template=None):
        self.formset_name_in_context = formset_name_in_context
        
        # crispy_forms/layout.py:302 requires us to have a fields property
        self.fields = []

        # Overrides class variable with an instance level variable
        if template:
            self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        formset = context[self.formset_name_in_context]
        return render_to_string(self.template, {'formset': formset})
