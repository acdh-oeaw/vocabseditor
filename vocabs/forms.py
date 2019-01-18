from dal import autocomplete
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, MultiField, HTML, ButtonHolder
from crispy_forms.bootstrap import *
from .models import *
from django.forms.models import inlineformset_factory
from .custom_layout_object import *


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


######################################################################
#   Classes  to store titles and descriptions for ConceptScheme
######################################################################

class ConceptSchemeTitleForm(forms.ModelForm):

    class Meta:
        model = ConceptSchemeTitle
        exclude = ()


ConceptSchemeTitleFormSet = inlineformset_factory(
    SkosConceptScheme, ConceptSchemeTitle,
    form=ConceptSchemeTitleForm,
    fields=['name', 'language'], extra=1, can_delete=True
    )


class ConceptSchemeDescriptionForm(forms.ModelForm):

    class Meta:
        model = ConceptSchemeDescription
        exclude = ()


ConceptSchemeDescriptionFormSet = inlineformset_factory(
    SkosConceptScheme, ConceptSchemeDescription,
    form=ConceptSchemeDescriptionForm,
    fields=['name', 'language'], extra=1, can_delete=True
    )


######################################################################
#
# SkosConceptScheme
#
######################################################################


class SkosConceptSchemeForm(forms.ModelForm):

    class Meta:
        model = SkosConceptScheme
        exclude = ['created_by', ]
        widgets = {
            'curator': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:user-autocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super(SkosConceptSchemeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('dc_title'),
                Field('dc_title_lang'),
                Fieldset('Add titles in other languages',
                    Formset('titles'))
                ,
                Field('dc_description'),
                Field('dc_description_lang'),
                Fieldset('Add descriptions in other languages',
                    Formset('descriptions'))
                ,
                Field('indentifier'),
                Field('dc_creator'),
                Field('dc_contributor'),
                Field('curator'),
                ButtonHolder(Submit('submit', 'save')),
            )
            )
        self.helper.render_required_fields = True


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


######################################################################
#   Classes  to store labels and notes for Collection
######################################################################

class CollectionLabelForm(forms.ModelForm):

    class Meta:
        model = CollectionLabel
        exclude = ()


CollectionLabelFormSet = inlineformset_factory(
    SkosCollection, CollectionLabel, form=CollectionLabelForm,
    fields=['name', 'label_type', 'language'],
    extra=1, can_delete=True
    )


class CollectionNoteForm(forms.ModelForm):

    class Meta:
        model = CollectionNote
        exclude = ()


CollectionNoteFormSet = inlineformset_factory(
    SkosCollection, CollectionNote, form=CollectionNoteForm,
    fields=['name', 'note_type', 'language'],
    extra=1, can_delete=True
    )

######################################################################
#
# SkosCollection
#
######################################################################

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
        self.helper.layout = Layout(
            Div(
                Field('name'),
                Field('label_lang'),
                Fieldset('Add more labels in other languages',
                    Formset('labels'))
                ,
                Field('scheme'),
                Field('creator'),
                Field('legacy_id'),
                # should have it or rely on a separate Class
                Field('skos_note'),
                Field('skos_note_lang'),
                Fieldset('Add more documentary notes',
                    Formset('notes'))
                ,
                ButtonHolder(Submit('submit', 'save')),
            )
            )
        self.helper.render_required_fields = True



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
                'scheme',
                'has_members__pref_label',
                css_id="basic_search_fields"
                ),
            )


######################################################################
#
# SkosLabel
#
######################################################################


class SkosLabelForm(forms.ModelForm):
    class Meta:
        model = SkosLabel
        exclude = ['created_by', ]
        widgets = {
            'scheme': autocomplete.ModelSelect2(
                url='vocabs-ac:skosconceptscheme-autocomplete'
            ),
        }

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

######################################################################
#
# SkosConcept
#
######################################################################

class SkosConceptForm(forms.ModelForm):
    class Meta:
        model = SkosConcept
        exclude = ['created_by', ]
        widgets = {
            'scheme': autocomplete.ModelSelect2(
                url='vocabs-ac:skosconceptscheme-autocomplete'),
            'broader_concept': autocomplete.ModelSelect2(
                url='vocabs-ac:skosconcept-nobroaderterm-autocomplete'),
            'other_label': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skoslabel-autocomplete'),
            'skos_broader': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-nobroaderterm-autocomplete'),
            'skos_narrower': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-nobroaderterm-autocomplete'),
            'skos_related': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-nobroaderterm-autocomplete'),
            'skos_broadmatch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-nobroaderterm-autocomplete'),
            'skos_narrowmatch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-nobroaderterm-autocomplete'),
            'skos_exactmatch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-nobroaderterm-autocomplete'),
            'skos_relatedmatch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-nobroaderterm-autocomplete'),
            'skos_closematch': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-nobroaderterm-autocomplete'),
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
                'other_label',
                'same_as_external',
                'source_description',
                css_id="basic_skos_fields"
                ),
            Accordion(
                AccordionGroup(
                    'SKOS semantic relationships',
                    'skos_broader',
                    'skos_narrower',
                    'skos_related',
                    'skos_broadmatch',
                    'skos_narrowmatch',
                    'skos_exactmatch',
                    'skos_relatedmatch',
                    'skos_closematch',
                    'legacy_id',
                    'notation',
                    'name_reverse',
                    css_id="advanced_skos_fields"
                ),
                 AccordionGroup(
                    'SKOS Documentary notes',
                    'skos_note',
                    'skos_note_lang',
                    'skos_scopenote',
                    'skos_scopenote_lang',
                    'skos_changenote',
                    'skos_editorialnote',
                    'skos_example',
                    'skos_historynote',
                    css_id="doc_skos_fields"
                ),
                css_id="main_accordion")
            )


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
                'scheme',
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
