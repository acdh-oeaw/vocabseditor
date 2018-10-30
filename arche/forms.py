# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, MultiField, HTML
from .models import Project, Collection, Resource


class ProjectFilterFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ProjectFilterFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.helper.form_tag = False
        self.add_input(Submit('Filter', 'Search'))
        self.layout = Layout(
            Fieldset(
                'Basic search options',
                'has_title',
                'description',
                css_id="basic_search_fields"
                ),
############# Uncomment accordion if there are advanced search options ############
            # Accordion(
            #     AccordionGroup(
            #         'Advanced search',
            #         css_id="more"
            #         ),
            #     )
            )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'save'),)


class CollectionFilterFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(CollectionFilterFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.helper.form_tag = False
        self.add_input(Submit('Filter', 'Search'))
        self.layout = Layout(
            Fieldset(
                'Basic search options',
                'has_title',
                'description',
                css_id="basic_search_fields"
                ),
############# Uncomment accordion if there are advanced search options ############
            # Accordion(
            #     AccordionGroup(
            #         'Advanced search',
            #         css_id="more"
            #         ),
            #     )
            )


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'save'),)


class ResourceFilterFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ResourceFilterFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.helper.form_tag = False
        self.add_input(Submit('Filter', 'Search'))
        self.layout = Layout(
            Fieldset(
                'Basic search options',
                'has_title',
                'description',
                'part_of',
                css_id="basic_search_fields"
                ),
############# Uncomment accordion if there are advanced search options ############
            # Accordion(
            #     AccordionGroup(
            #         'Advanced search',
            #         css_id="more"
            #         ),
            #     )
            )


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'save'),)
