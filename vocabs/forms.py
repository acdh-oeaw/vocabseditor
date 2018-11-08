from dal import autocomplete
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, MultiField, HTML
from crispy_forms.bootstrap import *
from .models import SkosConcept, SkosConceptScheme, SkosLabel, SkosCollection


class GenericFilterFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(GenericFilterFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.add_input(Submit('Filter', 'search'))


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'import'),)


class SkosConceptFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SkosConceptFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.helper.form_tag = False
        self.add_input(Submit('Filter', 'Search'))
        self.layout = Layout(
            Fieldset(
                'Basic search options',
                'pref_label',
                'collection',
                'broader_concept',
                'other_label',
                css_id="basic_search_fields"
                ),
            Accordion(
                AccordionGroup(
                    'Advanced search',
                    'top_concept',
                    'pref_label_lang',
                    'other_label__isoCode',
                    css_id="more"
                    ),
                )
            )


class SkosCollectionForm(forms.ModelForm):
    class Meta:
        model = SkosCollection
        exclude = ['created_by', ]
        widgets ={
            'scheme': autocomplete.ModelSelect2(
                url='vocabs-ac:skosconceptscheme-autocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super(SkosCollectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'save'),)


class SkosConceptForm(forms.ModelForm):
    class Meta:
        model = SkosConcept
        exclude = ['created_by', ]
        widgets = {
            'other_label': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skoslabel-autocomplete'),
            'skos_broader': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-autocomplete'),
            'skos_narrower': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-autocomplete'),
            'skos_related': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-autocomplete'),
            'skos_broadmatch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-autocomplete'),
            'skos_narrowmatch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-autocomplete'),
            'skos_exactmatch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-autocomplete'),
            'skos_relatedmatch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-autocomplete'),
            'skos_closematch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-autocomplete'),
            # 'scheme': autocomplete.ModelSelect2(
            #     url='vocabs-ac:skosconceptscheme-autocomplete'),
            'collection': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skoscollection-autocomplete')
        }

    def __init__(self, *args, **kwargs):
        super(SkosConceptForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'save'),)
        self.helper.layout = Layout(
            Fieldset(
                '',
                'pref_label',
                'pref_label_lang',
                'scheme',
                'top_concept',
                'collection',
                'definition',
                'definition_lang',
                'broader_concept',
                'dc_creator',
                'source_description',
                'same_as_external',
                css_id="basic_skos_fields"
                ),
            Accordion(
                AccordionGroup(
                    'Advanced fields',
                    'other_label',
                    'notation',
                    'skos_broader',
                    'skos_narrower',
                    'skos_related',
                    'skos_broadmatch',
                    'skos_narrowmatch',
                    'skos_exactmatch',
                    'skos_relatedmatch',
                    'skos_closematch',
                    'legacy_id',
                    'name_reverse',
                    'skos_note',
                    'skos_note_lang',
                    'skos_scopenote',
                    'skos_scopenote_lang',
                    'skos_changenote',
                    'skos_editorialnote',
                    'skos_example',
                    'skos_historynote',
                    'namespace',
                    css_id="advanced_skos_fields"
                ),
                )
            )


class SkosConceptSchemeForm(forms.ModelForm):
    class Meta:
        model = SkosConceptScheme
        #fields = "__all__"
        exclude = ['created_by', ]

    def __init__(self, *args, **kwargs):
        super(SkosConceptSchemeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'save'),)


class SkosConceptSchemeFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SkosConceptSchemeFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.helper.form_tag = False
        self.add_input(Submit('Filter', 'Search'))
        self.layout = Layout(
            Fieldset(
                '',
                'dc_title',
                'dc_creator',
                css_id="basic_search_fields"
                ),
            )


class SkosLabelForm(forms.ModelForm):
    class Meta:
        model = SkosLabel
        exclude = ['created_by', ]

    def __init__(self, *args, **kwargs):
        super(SkosLabelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.add_input(Submit('submit', 'save'),)


class SkosLabelFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SkosLabelFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.helper.form_tag = False
        self.add_input(Submit('Filter', 'Search'))


class SkosCollectionFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(SkosCollectionFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.helper.form_tag = False
        self.add_input(Submit('Filter', 'Search'))
        self.layout = Layout(
            Fieldset(
                '',
                'name',
                'creator',
                'has_members__pref_label',
                css_id="basic_search_fields"
                ),
            )
