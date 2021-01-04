from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django_tables2 import RequestConfig
from .models import SkosConcept, SkosConceptScheme, SkosCollection
from .forms import *
from .tables import *
from .filters import SkosConceptListFilter, SkosConceptSchemeListFilter, SkosCollectionListFilter
from browsing.browsing_utils import GenericListView, BaseCreateView, BaseUpdateView
from .rdf_utils import *
from django.shortcuts import render
from django.http import HttpResponse
import time
import datetime
from guardian.shortcuts import get_objects_for_user
from django.contrib.auth.decorators import login_required, permission_required
from reversion.models import Version
from django.db import transaction
from django.shortcuts import redirect
from .skos_import import *
from django.contrib import messages


class BaseDetailView(DetailView):

    def get_queryset(self, **kwargs):
        qs = get_objects_for_user(self.request.user,
                                  perms=[
                                      'view_{}'.format(self.model.__name__.lower()),
                                      'change_{}'.format(self.model.__name__.lower()),
                                      'delete_{}'.format(self.model.__name__.lower()),
                                  ],
                                  klass=self.model)
        return qs

    def get_context_data(self, **kwargs):
        context = super(BaseDetailView, self).get_context_data(**kwargs)
        context['history'] = Version.objects.get_for_object(self.object)
        return context


class BaseDeleteView(DeleteView):

    def get_queryset(self, **kwargs):
        qs = get_objects_for_user(self.request.user,
                                  perms=[
                                      'view_{}'.format(self.model.__name__.lower()),
                                      'change_{}'.format(self.model.__name__.lower()),
                                      'delete_{}'.format(self.model.__name__.lower()),
                                  ],
                                  klass=self.model)
        return qs


######################################################################
#
# SkosConceptScheme
#
######################################################################

class SkosConceptSchemeListView(GenericListView):
    model = SkosConceptScheme
    table_class = SkosConceptSchemeTable
    filter_class = SkosConceptSchemeListFilter
    formhelper_class = SkosConceptSchemeFormHelper
    init_columns = [
        'id',
        'title',
    ]

    def get_all_cols(self):
        all_cols = list(self.table_class.base_columns.keys())
        return all_cols

    def get_context_data(self, **kwargs):
        context = super(SkosConceptSchemeListView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        togglable_colums = [x for x in self.get_all_cols() if x not in self.init_columns]
        context['togglable_colums'] = togglable_colums
        return context

    def get_table(self, **kwargs):
        table = super(GenericListView, self).get_table()
        RequestConfig(self.request, paginate={
            'page': 1, 'per_page': self.paginate_by
        }).configure(table)
        default_cols = self.init_columns
        all_cols = self.get_all_cols()
        selected_cols = self.request.GET.getlist("columns") + default_cols
        exclude_vals = [x for x in all_cols if x not in selected_cols]
        table.exclude = exclude_vals
        return table


class SkosConceptSchemeDetailView(BaseDetailView):
    model = SkosConceptScheme
    template_name = 'vocabs/skosconceptscheme_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SkosConceptSchemeDetailView, self).get_context_data(**kwargs)
        context["concepts"] = SkosConcept.objects.filter(scheme=self.kwargs.get('pk'))
        return context


class SkosConceptSchemeCreate(BaseCreateView):
    model = SkosConceptScheme
    form_class = SkosConceptSchemeForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosConceptSchemeCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['titles'] = ConceptSchemeTitleFormSet(self.request.POST)
            data['descriptions'] = ConceptSchemeDescriptionFormSet(self.request.POST)
            data['sources'] = ConceptSchemeSourceFormSet(self.request.POST)
        else:
            data['titles'] = ConceptSchemeTitleFormSet()
            data['descriptions'] = ConceptSchemeDescriptionFormSet()
            data['sources'] = ConceptSchemeSourceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        titles = context['titles']
        descriptions = context['descriptions']
        sources = context['sources']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            # cs should be saved first because fk object are related to it
            self.object = form.save(commit=False)
            if titles.is_valid():
                titles.instance = self.object
                titles.save(commit=False)
            else:
                return super(SkosConceptSchemeCreate, self).form_invalid(form)
            if descriptions.is_valid():
                descriptions.instance = self.object
                descriptions.save(commit=False)
            else:
                return super(SkosConceptSchemeCreate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save(commit=False)
            else:
                return super(SkosConceptSchemeCreate, self).form_invalid(form)
            self.object = form.save()
            titles.save()
            descriptions.save()
            sources.save()

        return super(SkosConceptSchemeCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vocabs:skosconceptscheme_detail', kwargs={'pk': self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptSchemeCreate, self).dispatch(*args, **kwargs)


class SkosConceptSchemeUpdate(BaseUpdateView):
    model = SkosConceptScheme
    form_class = SkosConceptSchemeForm
    permission_required = (
        'view_skosconceptscheme',
        'change_skosconceptscheme',
        'delete_skosconceptscheme',
    )
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosConceptSchemeUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['titles'] = ConceptSchemeTitleFormSet(
                self.request.POST, instance=self.object
            )
            data['descriptions'] = ConceptSchemeDescriptionFormSet(
                self.request.POST, instance=self.object
            )
            data['sources'] = ConceptSchemeSourceFormSet(
                self.request.POST, instance=self.object
            )
        else:
            data['titles'] = ConceptSchemeTitleFormSet(instance=self.object)
            data['descriptions'] = ConceptSchemeDescriptionFormSet(instance=self.object)
            data['sources'] = ConceptSchemeSourceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        titles = context['titles']
        descriptions = context['descriptions']
        sources = context['sources']
        with transaction.atomic():
            if titles.is_valid():
                titles.instance = self.object
                titles.save()
            else:
                # raise forms.ValidationError("Both fields should be filled")
                return super(SkosConceptSchemeUpdate, self).form_invalid(form)
            if descriptions.is_valid():
                descriptions.instance = self.object
                descriptions.save()
            else:
                return super(SkosConceptSchemeUpdate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save()
            else:
                return super(SkosConceptSchemeUpdate, self).form_invalid(form)
        return super(SkosConceptSchemeUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vocabs:skosconceptscheme_detail', kwargs={'pk': self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptSchemeUpdate, self).dispatch(*args, **kwargs)


class SkosConceptSchemeDelete(BaseDeleteView):
    model = SkosConceptScheme
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('vocabs:browse_schemes')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptSchemeDelete, self).dispatch(*args, **kwargs)


######################################################################
#
# SkosCollection
#
######################################################################

class SkosCollectionListView(GenericListView):
    model = SkosCollection
    table_class = SkosCollectionTable
    filter_class = SkosCollectionListFilter
    formhelper_class = SkosCollectionFormHelper
    init_columns = [
        'id',
        'name',
        'scheme',
    ]

    def get_all_cols(self):
        all_cols = list(self.table_class.base_columns.keys())
        return all_cols

    def get_context_data(self, **kwargs):
        context = super(SkosCollectionListView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        togglable_colums = [x for x in self.get_all_cols() if x not in self.init_columns]
        context['togglable_colums'] = togglable_colums
        return context

    def get_table(self, **kwargs):
        table = super(GenericListView, self).get_table()
        RequestConfig(self.request, paginate={
            'page': 1, 'per_page': self.paginate_by
        }).configure(table)
        default_cols = self.init_columns
        all_cols = self.get_all_cols()
        selected_cols = self.request.GET.getlist("columns") + default_cols
        exclude_vals = [x for x in all_cols if x not in selected_cols]
        table.exclude = exclude_vals
        return table


class SkosCollectionDetailView(BaseDetailView):
    model = SkosCollection
    template_name = 'vocabs/skoscollection_detail.html'


class SkosCollectionCreate(BaseCreateView):
    model = SkosCollection
    form_class = SkosCollectionForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosCollectionCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['labels'] = CollectionLabelFormSet(self.request.POST)
            data['notes'] = CollectionNoteFormSet(self.request.POST)
            data['sources'] = CollectionSourceFormSet(self.request.POST)
        else:
            data['labels'] = CollectionLabelFormSet()
            data['notes'] = CollectionNoteFormSet()
            data['sources'] = CollectionSourceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        labels = context['labels']
        notes = context['notes']
        sources = context['sources']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save(commit=False)
            if labels.is_valid():
                labels.instance = self.object
                labels.save(commit=False)
            else:
                return super(SkosCollectionCreate, self).form_invalid(form)
            if notes.is_valid():
                notes.instance = self.object
                notes.save(commit=False)
            else:
                return super(SkosCollectionCreate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save(commit=False)
            else:
                return super(SkosCollectionCreate, self).form_invalid(form)
            self.object = form.save()
            labels.save()
            notes.save()
            sources.save()
        return super(SkosCollectionCreate, self).form_valid(form)

    def get_initial(self):
        initial = super(SkosCollectionCreate, self).get_initial()
        if self.request.GET.get('scheme'):
            initial['scheme'] = SkosConceptScheme.objects.get(pk=self.request.GET.get('scheme'))
        return initial

    def get_success_url(self):
        return reverse_lazy('vocabs:skoscollection_detail', kwargs={'pk': self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosCollectionCreate, self).dispatch(*args, **kwargs)


class SkosCollectionUpdate(BaseUpdateView):
    model = SkosCollection
    form_class = SkosCollectionForm
    permission_required = (
        'view_skoscollection',
        'change_skoscollection',
        'delete_skoscollection',
    )
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosCollectionUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['labels'] = CollectionLabelFormSet(self.request.POST, instance=self.object)
            data['notes'] = CollectionNoteFormSet(self.request.POST, instance=self.object)
            data['sources'] = CollectionSourceFormSet(self.request.POST, instance=self.object)
        else:
            data['labels'] = CollectionLabelFormSet(instance=self.object)
            data['notes'] = CollectionNoteFormSet(instance=self.object)
            data['sources'] = CollectionSourceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        labels = context['labels']
        notes = context['notes']
        sources = context['sources']
        with transaction.atomic():
            if labels.is_valid():
                labels.instance = self.object
                labels.save()
            else:
                return super(SkosCollectionUpdate, self).form_invalid(form)
            if notes.is_valid():
                notes.instance = self.object
                notes.save()
            else:
                return super(SkosCollectionUpdate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save()
            else:
                return super(SkosCollectionUpdate, self).form_invalid(form)
        return super(SkosCollectionUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vocabs:skoscollection_detail', kwargs={'pk': self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosCollectionUpdate, self).dispatch(*args, **kwargs)


class SkosCollectionDelete(BaseDeleteView):
    model = SkosCollection
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('vocabs:browse_skoscollections')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosCollectionDelete, self).dispatch(*args, **kwargs)


######################################################################
#
# SkosConcept
#
######################################################################

class SkosConceptListView(GenericListView):
    model = SkosConcept
    table_class = SkosConceptTable
    filter_class = SkosConceptListFilter
    formhelper_class = SkosConceptFormHelper
    init_columns = [
        'id',
        'pref_label',
        'scheme',
    ]

    def get_queryset(self, **kwargs):
        qs = super(SkosConceptListView, self).get_queryset()
        return qs.order_by('id')


class SkosConceptDetailView(BaseDetailView):
    model = SkosConcept
    template_name = 'vocabs/skosconcept_detail.html'
    success_url = None

    def get_context_data(self, **kwargs):
        context = super(SkosConceptDetailView, self).get_context_data(**kwargs)
        return context


class SkosConceptCreate(BaseCreateView):
    model = SkosConcept
    form_class = SkosConceptForm

    def get_context_data(self, **kwargs):
        data = super(SkosConceptCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['labels'] = ConceptLabelFormSet(self.request.POST)
            data['notes'] = ConceptNoteFormSet(self.request.POST)
            data['sources'] = ConceptSourceFormSet(self.request.POST)
        else:
            data['labels'] = ConceptLabelFormSet()
            data['notes'] = ConceptNoteFormSet()
            data['sources'] = ConceptSourceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        labels = context['labels']
        notes = context['notes']
        sources = context['sources']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save(commit=False)
            if labels.is_valid():
                labels.instance = self.object
                labels.save(commit=False)
            else:
                return super(SkosConceptCreate, self).form_invalid(form)
            if notes.is_valid():
                notes.instance = self.object
                notes.save(commit=False)
            else:
                return super(SkosConceptCreate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save(commit=False)
            else:
                return super(SkosConceptCreate, self).form_invalid(form)
            self.object = form.save()
            labels.save()
            notes.save()
            sources.save()
        return super(SkosConceptCreate, self).form_valid(form)

    def get_initial(self):
        initial = super(SkosConceptCreate, self).get_initial()
        if self.request.GET.get('scheme'):
            initial['scheme'] = SkosConceptScheme.objects.get(pk=self.request.GET.get('scheme'))
        if self.request.GET.get('collection'):
            initial['collection'] = SkosCollection.objects.get(pk=self.request.GET.get('collection'))
        return initial

    def get_success_url(self):
        return reverse_lazy('vocabs:skosconcept_detail', kwargs={'pk': self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptCreate, self).dispatch(*args, **kwargs)


class SkosConceptUpdate(BaseUpdateView):
    model = SkosConcept
    form_class = SkosConceptForm
    permission_required = (
        'view_skosconcept',
        'change_skosconcept',
        'delete_skosconcept',
    )
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosConceptUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['labels'] = ConceptLabelFormSet(self.request.POST, instance=self.object)
            data['notes'] = ConceptNoteFormSet(self.request.POST, instance=self.object)
            data['sources'] = ConceptSourceFormSet(self.request.POST, instance=self.object)
        else:
            data['labels'] = ConceptLabelFormSet(instance=self.object)
            data['notes'] = ConceptNoteFormSet(instance=self.object)
            data['sources'] = ConceptSourceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        labels = context['labels']
        notes = context['notes']
        sources = context['sources']
        with transaction.atomic():
            if labels.is_valid():
                labels.instance = self.object
                labels.save()
            else:
                return super(SkosConceptUpdate, self).form_invalid(form)
            if notes.is_valid():
                notes.instance = self.object
                notes.save()
            else:
                return super(SkosConceptUpdate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save()
            else:
                return super(SkosConceptUpdate, self).form_invalid(form)
        return super(SkosConceptUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vocabs:skosconcept_detail', kwargs={'pk': self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptUpdate, self).dispatch(*args, **kwargs)


class SkosConceptDelete(BaseDeleteView):
    model = SkosConcept
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('vocabs:browse_vocabs')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptDelete, self).dispatch(*args, **kwargs)


###################################################
# SkosConcepts download as one ConceptScheme
###################################################

class SkosConceptDL(GenericListView):
    model = SkosConcept
    table_class = SkosConceptTable
    filter_class = SkosConceptListFilter
    formhelper_class = SkosConceptFormHelper

    def render_to_response(self, context):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
        response = HttpResponse(content_type='application/xml; charset=utf-8')
        filename = "download_{}".format(timestamp)
        get_format = self.request.GET.get('format', default='pretty-xml')
        if get_format == 'turtle':
            response['Content-Disposition'] = 'attachment; filename="{}.ttl"'.format(filename)
        else:
            response['Content-Disposition'] = 'attachment; filename="{}.rdf"'.format(filename)
        g = graph_construct_qs(self.get_queryset())
        result = g.serialize(destination=response, format=get_format)
        return response


###################################################
# SKOS vocabulary upload
###################################################

@login_required
def file_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_format = file.name.split('.')[-1]
            if file_format in ['ttl', 'rdf']:
                if file_format == 'ttl':
                    skos_vocab = SkosImporter(file=file, file_format="ttl", language=form.cleaned_data['language'])
                else:
                    skos_vocab = SkosImporter(file=file, language=form.cleaned_data['language'])
                try:
                    skos_vocab.upload_data(user=request.user.username)
                    return redirect('vocabs:browse_schemes')
                except Exception as error:
                    messages.error(request, error)
            else:
                messages.error(request, "Upload rdf or ttl file")
    else:
        form = UploadFileForm()
    return render(request, 'vocabs/upload.html', {'form': form})
