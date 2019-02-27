from dal import autocomplete
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML, ButtonHolder
from crispy_forms.bootstrap import *
from .models import *
from django.forms.models import inlineformset_factory
from .custom_layout_object import *
from mptt.forms import TreeNodeChoiceField
from django.forms import BaseInlineFormSet


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


def custom_name_errors(field_name):
    name_errors = {}
    name_errors['required'] = '{} is required when language provided'.format(field_name)
    name_errors['invalid']: 'Enter a valid value'
    return name_errors


def custom_lang_errors(field_name):
    lang_errors = {}
    lang_errors['required'] = 'Language is required when {} provided'.format(field_name.lower())
    lang_errors['invalid']: 'Enter a valid value'
    return lang_errors


######################################################################
#   Classes  to store titles and descriptions for ConceptScheme
######################################################################


# We also want to verify that all formsets have both fields a name and a language filled out.
# We could simply set the fields as required on the form itself,
# however this will prevent our users from submitting empty forms,
# which is not the behaviour we’re looking for here. From a usability perspective, it would be better
# to simply ignore forms that are completely empty, raising errors only if a form is partially incomplete.

class CustomInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(CustomInlineFormSet, self).clean()
        if any(self.errors):
            return
        for form in self.forms:
            if form.cleaned_data:
                name = form.cleaned_data['name']
                language = form.cleaned_data['language']
                # Check that formset has both fields - a name and a language - filled out
                if name and not language:
                    raise forms.ValidationError(
                        'All names must have a lanaguge.'
                    )
                elif language and not name:
                    raise forms.ValidationError(
                        'All languages must have a name.'
                    )



class ConceptSchemeTitleForm(forms.ModelForm):
    name = forms.CharField(
        label=ConceptSchemeTitle._meta.get_field('name').verbose_name,
        help_text=ConceptSchemeTitle._meta.get_field('name').help_text,
        error_messages=custom_name_errors(
            field_name=ConceptSchemeTitle._meta.get_field('name').verbose_name
            )
    )
    language = forms.CharField(
        label=ConceptSchemeTitle._meta.get_field('language').verbose_name,
        help_text=ConceptSchemeTitle._meta.get_field('language').help_text,
        error_messages=custom_lang_errors(
            field_name=ConceptSchemeTitle._meta.get_field('name').verbose_name
            )
    )

    def __init__(self, *args, **kwargs): 
        super(ConceptSchemeTitleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'

    class Meta:
        model = ConceptSchemeTitle
        exclude = ()


ConceptSchemeTitleFormSet = inlineformset_factory(
    SkosConceptScheme, ConceptSchemeTitle,
    form=ConceptSchemeTitleForm,
    fields=['name', 'language'], extra=1, can_delete=True
    )


class ConceptSchemeDescriptionForm(forms.ModelForm):
    name = forms.CharField(
        label=ConceptSchemeDescription._meta.get_field('name').verbose_name,
        help_text=ConceptSchemeDescription._meta.get_field('name').help_text,
        error_messages=custom_name_errors(
            field_name=ConceptSchemeDescription._meta.get_field('name').verbose_name
            )
    )
    language = forms.CharField(
        label=ConceptSchemeDescription._meta.get_field('language').verbose_name,
        help_text=ConceptSchemeDescription._meta.get_field('language').help_text,
        error_messages=custom_lang_errors(
            field_name=ConceptSchemeDescription._meta.get_field('name').verbose_name
            )
    )

    def __init__(self, *args, **kwargs):
        super(ConceptSchemeDescriptionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'

    class Meta:
        model = ConceptSchemeDescription
        exclude = ()


ConceptSchemeDescriptionFormSet = inlineformset_factory(
    SkosConceptScheme, ConceptSchemeDescription,
    form=ConceptSchemeDescriptionForm,
    fields=['name', 'language'], extra=1, can_delete=True
    )


class ConceptSchemeSourceForm(forms.ModelForm):
    name = forms.CharField(
        label=ConceptSchemeSource._meta.get_field('name').verbose_name,
        help_text=ConceptSchemeSource._meta.get_field('name').help_text,
        error_messages=custom_name_errors(
            field_name=ConceptSchemeSource._meta.get_field('name').verbose_name
            )
    )
    language = forms.CharField(
        label=ConceptSchemeSource._meta.get_field('language').verbose_name,
        help_text=ConceptSchemeSource._meta.get_field('language').help_text,
        error_messages=custom_lang_errors(
            field_name=ConceptSchemeSource._meta.get_field('name').verbose_name
            )
    )

    def __init__(self, *args, **kwargs):
        super(ConceptSchemeSourceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'

    class Meta:
        model = ConceptSchemeSource
        exclude = ()


ConceptSchemeSourceFormSet = inlineformset_factory(
    SkosConceptScheme, ConceptSchemeSource, form=ConceptSchemeSourceForm,
    fields=['name', 'language'],
    extra=1, can_delete=True
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
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'
        self.helper.layout = Layout(
            Div(
                Field('title'),
                Field('title_lang'),
                # Accordion(
                # AccordionGroup('Add titles in other languages',
                #     Formset('titles'), css_class="formset-div")),




                Fieldset('Add titles in other languages',
                    Formset('titles'), css_class="formset-div")
                ,
                Fieldset('Add description',
                    Formset('descriptions'), css_class="formset-div")
                ,
                Field('indentifier'),
                Field('language'),
                Field('creator'),
                Field('contributor'),
                Field('publisher'),
                Field('license'),
                Field('owner'),
                Field('subject'),
                Field('relation'),
                Field('coverage'),
                Fieldset('Add source information',
                    Formset('sources'), css_class="formset-div")
                ,
                Field('version'),
                Field('legacy_id'),
                Field('date_issued', placeholder="YYYY-MM-DD"),
                Field('curator'),
                HTML("<br>"),
                ButtonHolder(Submit('submit', 'save')),
            )
            )


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
                'title',
                'creator',
                css_id="basic_search_fields"
                ),
            )


######################################################################
#   Classes  to store labels and notes for Collection
######################################################################

class CollectionLabelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CollectionLabelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'

    class Meta:
        model = CollectionLabel
        exclude = ()


CollectionLabelFormSet = inlineformset_factory(
    SkosCollection, CollectionLabel, form=CollectionLabelForm,
    fields=['name', 'label_type', 'language'],
    extra=1, can_delete=True
    )


class CollectionNoteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CollectionNoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'

    class Meta:
        model = CollectionNote
        exclude = ()


CollectionNoteFormSet = inlineformset_factory(
    SkosCollection, CollectionNote, form=CollectionNoteForm,
    fields=['name', 'note_type', 'language'],
    extra=1, can_delete=True
    )


class CollectionSourceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CollectionSourceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'

    class Meta:
        model = CollectionSource
        exclude = ()


CollectionSourceFormSet = inlineformset_factory(
    SkosCollection, CollectionSource, form=CollectionSourceForm,
    fields=['name', 'language'],
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
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'
        self.helper.layout = Layout(
            Div(
                Field('name'),
                Field('label_lang'),
                Fieldset('Add more labels in other languages',
                    Formset('labels'), css_class="formset-div")
                ,
                Field('scheme'),
                Field('creator'),
                Field('contributor'),
                Field('legacy_id'),
                Fieldset('Add more documentary notes',
                    Formset('notes'), css_class="formset-div")
                ,
                Fieldset('Add source information',
                    Formset('sources'), css_class="formset-div")
                ,
                HTML("<br>"),
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
#   Classes  to store labels, notes and sources for Concept
######################################################################

class ConceptLabelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ConceptLabelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'

    class Meta:
        model = ConceptLabel
        exclude = ()


ConceptLabelFormSet = inlineformset_factory(
    SkosConcept, ConceptLabel, form=ConceptLabelForm,
    fields=['name', 'label_type', 'language'],
    extra=1, can_delete=True
    )


class ConceptNoteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ConceptNoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'

    class Meta:
        model = ConceptNote
        exclude = ()


ConceptNoteFormSet = inlineformset_factory(
    SkosConcept, ConceptNote, form=ConceptNoteForm,
    fields=['name', 'note_type', 'language'],
    extra=1, can_delete=True
    )


class ConceptSourceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ConceptSourceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'

    class Meta:
        model = ConceptSource
        exclude = ()


ConceptSourceFormSet = inlineformset_factory(
    SkosConcept, ConceptSource, form=ConceptSourceForm,
    fields=['name', 'language'],
    extra=1, can_delete=True
    )


######################################################################
#
# SkosConcept
#
######################################################################

class SkosConceptForm(forms.ModelForm):
    broader_concept = TreeNodeChoiceField(
        queryset=SkosConcept.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='vocabs-ac:skosconcept-autocomplete',
            forward=['scheme']
        ),
        help_text="A concept with a broader meaning that a current concept inherits from",
        required=False
    )
    collection = forms.ModelMultipleChoiceField(
        queryset=SkosCollection.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skoscollection-autocomplete',
                forward=['scheme']
        ),
        help_text="member of skos:Collection",
        required=False
    )
    skos_broadmatch = forms.ModelMultipleChoiceField(
        queryset=SkosConcept.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-extmatch-autocomplete',
                forward=['scheme']
        ),
        help_text=SkosConcept._meta.get_field('skos_broadmatch').help_text,
        label=SkosConcept._meta.get_field('skos_broadmatch').verbose_name,
        required=False
    )
    skos_narrowmatch = forms.ModelMultipleChoiceField(
        queryset=SkosConcept.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-extmatch-autocomplete',
                forward=['scheme']
        ),
        help_text=SkosConcept._meta.get_field('skos_narrowmatch').help_text,
        label=SkosConcept._meta.get_field('skos_narrowmatch').verbose_name,
        required=False
    )
    skos_exactmatch = forms.ModelMultipleChoiceField(
        queryset=SkosConcept.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-extmatch-autocomplete',
                forward=['scheme']
        ),
        help_text=SkosConcept._meta.get_field('skos_exactmatch').help_text,
        label=SkosConcept._meta.get_field('skos_exactmatch').verbose_name,
        required=False
    )
    skos_relatedmatch = forms.ModelMultipleChoiceField(
        queryset=SkosConcept.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-extmatch-autocomplete',
                forward=['scheme']
        ),
        help_text=SkosConcept._meta.get_field('skos_relatedmatch').help_text,
        label=SkosConcept._meta.get_field('skos_relatedmatch').verbose_name,
        required=False
    )
    skos_closematch = forms.ModelMultipleChoiceField(
        queryset=SkosConcept.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-extmatch-autocomplete',
                forward=['scheme']
        ),
        help_text=SkosConcept._meta.get_field('skos_closematch').help_text,
        label=SkosConcept._meta.get_field('skos_closematch').verbose_name,
        required=False
    )

    class Meta:
        model = SkosConcept
        exclude = ['created_by', ]
        widgets = {
            'scheme': autocomplete.ModelSelect2(
                url='vocabs-ac:skosconceptscheme-autocomplete'),
            'skos_related': autocomplete.ModelSelect2Multiple(
                url='vocabs-ac:skosconcept-autocomplete'),
        }


    def __init__(self, *args, **kwargs):
        super(SkosConceptForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2 create-label'
        self.helper.field_class = 'col-md-10'
        self.helper.layout = Layout(
            Div(
                Field('pref_label'),
                Field('pref_label_lang'),
                Fieldset('Add more labels',
                    Formset('labels'), css_class="formset-div")
                ,
                Field('scheme'),
                Field('top_concept'),
                Field('collection'),
                Field('broader_concept'),
                Fieldset('Add documentary notes',
                    Formset('notes'), css_class="formset-div")
                ,
                Field('creator'),
                Field('contributor'),
                Field('same_as_external'),
                Field('notation'),
                Field('legacy_id'),
                Fieldset('Add source information',
                    Formset('sources'), css_class="formset-div")
                ,
                Accordion(
                AccordionGroup(
                    'Add SKOS semantic relationships',
                    'skos_related',
                    'skos_broadmatch',
                    'skos_narrowmatch',
                    'skos_exactmatch',
                    'skos_relatedmatch',
                    'skos_closematch',
                    css_id="advanced_skos_fields"
                ),
                ),
                HTML("<br>"),
                ButtonHolder(Submit('submit', 'save')),
            )
            )
        self.helper.render_required_fields = True


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
                '',
                'pref_label',
                'scheme',
                'top_concept',
                'collection',
                'broader_concept',
                css_id="basic_search_fields"
                ),
            )
