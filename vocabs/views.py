from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django_tables2 import SingleTableView, RequestConfig
from .models import SkosConcept, SkosConceptScheme, SkosLabel, SkosCollection
from .forms import *
from .tables import *
from .filters import SkosConceptListFilter, SkosConceptSchemeListFilter, SkosLabelListFilter, SkosCollectionListFilter
from browsing.browsing_utils import GenericListView, BaseCreateView, BaseUpdateView
from .rdf_utils import *
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef, RDFS, ConjunctiveGraph
from rdflib.namespace import DC, FOAF, RDFS, SKOS
import time
import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin
from guardian.shortcuts import get_objects_for_user, get_perms_for_model
from guardian.core import ObjectPermissionChecker
from django.contrib.auth.decorators import login_required, permission_required
from guardian.decorators import permission_required_or_403
from django.contrib.auth.mixins import UserPassesTestMixin


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


#####################################################
#   SkosCollection
#####################################################


class SkosCollectionListView(GenericListView):
    model = SkosCollection
    table_class = SkosCollectionTable
    filter_class = SkosCollectionListFilter
    formhelper_class = SkosCollectionFormHelper
    init_columns = [
        'id',
        'name',
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

    def form_valid(self, form):
        object = form.save(commit=False)
        object.created_by = self.request.user
        object.save()
        return super(SkosCollectionCreate, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosCollectionCreate, self).dispatch(*args, **kwargs)


class SkosCollectionUpdate(BaseUpdateView):

    model = SkosCollection
    form_class = SkosCollectionForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosCollectionUpdate, self).dispatch(*args, **kwargs)


class SkosCollectionDelete(DeleteView):
    model = SkosCollection
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('vocabs:browse_skoscollections')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosCollectionDelete, self).dispatch(*args, **kwargs)


#####################################################
#   Concept
#####################################################


class SkosConceptListView(GenericListView):
    model = SkosConcept
    table_class = SkosConceptTable
    filter_class = SkosConceptListFilter
    formhelper_class = SkosConceptFormHelper
    init_columns = [
        'id',
        'pref_label',
        'broader_concept',
    ]


class SkosConceptDetailView(BaseDetailView):

    model = SkosConcept
    template_name = 'vocabs/skosconcept_detail.html'


class SkosConceptCreate(BaseCreateView):

    model = SkosConcept
    form_class = SkosConceptForm

    def form_valid(self, form):
        object = form.save(commit=False)
        object.created_by = self.request.user
        object.save()
        return super(SkosConceptCreate, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptCreate, self).dispatch(*args, **kwargs)


class SkosConceptUpdate(BaseUpdateView):

    model = SkosConcept
    form_class = SkosConceptForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptUpdate, self).dispatch(*args, **kwargs)


class SkosConceptDelete(DeleteView):
    model = SkosConcept
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('vocabs:browse_vocabs')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptDelete, self).dispatch(*args, **kwargs)


#####################################################
#   ConceptScheme
#####################################################

class SkosConceptSchemeListView(GenericListView):
    model = SkosConceptScheme
    table_class = SkosConceptSchemeTable
    filter_class = SkosConceptSchemeListFilter
    formhelper_class = SkosConceptSchemeFormHelper
    init_columns = [
        'id',
        'dc_title',
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
    # add get_objects_for_user or permission checker

    model = SkosConceptScheme
    template_name = 'vocabs/skosconceptscheme_detail.html'

    # def get_queryset(self, **kwargs):
    #     qs = get_objects_for_user(self.request.user,
    #         perms=[
    #         'view_skosconceptscheme',
    #         'change_skosconceptscheme',
    #         'delete_skosconceptscheme'
    #         ],
    #         klass=SkosConceptScheme)
    #     return qs

    def get_context_data(self, **kwargs):
        context = super(SkosConceptSchemeDetailView, self).get_context_data(**kwargs)
        context["concepts"] = SkosConcept.objects.filter(scheme=self.kwargs.get('pk'))
        return context


class SkosConceptSchemeCreate(BaseCreateView):

    model = SkosConceptScheme
    form_class = SkosConceptSchemeForm

    # save the creator of Concept Scheme automatically when CS is created
    # the user can't change it, but this can be changed in admin
    def form_valid(self, form):
        object = form.save(commit=False)
        object.created_by = self.request.user
        object.save()
        return super(SkosConceptSchemeCreate, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptSchemeCreate, self).dispatch(*args, **kwargs)


class SkosConceptSchemeUpdate(BaseUpdateView):
    # add get_objects_for_user or permission checker

    model = SkosConceptScheme
    form_class = SkosConceptSchemeForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptSchemeUpdate, self).dispatch(*args, **kwargs)


class SkosConceptSchemeDelete(DeleteView):
    # add get_objects_for_user or permission checker
    model = SkosConceptScheme
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('vocabs:browse_schemes')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptSchemeDelete, self).dispatch(*args, **kwargs)


###################################################
# SkosLabel
###################################################


class SkosLabelListView(GenericListView):
    model = SkosLabel
    table_class = SkosLabelTable
    filter_class = SkosLabelListFilter
    formhelper_class = SkosLabelFormHelper
    init_columns = [
        'id',
        'name',
    ]

    def get_all_cols(self):
        all_cols = list(self.table_class.base_columns.keys())
        return all_cols

    def get_context_data(self, **kwargs):
        context = super(SkosLabelListView, self).get_context_data()
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


class SkosLabelDetailView(BaseDetailView):

    model = SkosLabel
    template_name = 'vocabs/skoslabel_detail.html'


class SkosLabelCreate(BaseCreateView):

    model = SkosLabel
    form_class = SkosLabelForm

    def form_valid(self, form):
        object = form.save(commit=False)
        object.created_by = self.request.user
        object.save()
        return super(SkosLabelCreate, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosLabelCreate, self).dispatch(*args, **kwargs)


class SkosLabelUpdate(BaseUpdateView):

    model = SkosLabel
    form_class = SkosLabelForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosLabelUpdate, self).dispatch(*args, **kwargs)


class SkosLabelDelete(DeleteView):
    model = SkosLabel
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('vocabs:browse_skoslabels')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosLabelDelete, self).dispatch(*args, **kwargs)


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
        response['Content-Disposition'] = 'attachment; filename="{}.rdf"'.format(filename)
        g = graph_construct_qs(self.get_queryset())
        get_format = self.request.GET.get('format', default='pretty-xml')
        result = g.serialize(destination=response, format=get_format)
        return response