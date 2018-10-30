import requests
import re
import time
import datetime
from django.http import HttpResponse
from django.shortcuts import (render, render_to_response, get_object_or_404, redirect)
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_tables2 import RequestConfig
from .models import Place, AlternativeName, Institution, Person
from .forms import *
from .serializer_arche import *
from .tables import PersonTable, InstitutionTable, PlaceTable, AlternativeNameTable
from .filters import (
    PersonListFilter,
    InstitutionListFilter,
    PlaceListFilter,
    AlternativeNameListFilter,
)
from browsing.browsing_utils import GenericListView, BaseCreateView, BaseUpdateView
from reversion.models import Version


class InstitutionListView(GenericListView):
    model = Institution
    table_class = InstitutionTable
    filter_class = InstitutionListFilter
    formhelper_class = InstitutionFilterFormHelper
    init_columns = [
        'id',
        'written_name',
    ]


class InstitutionRDFView(GenericListView):
    model = Institution
    table_class = InstitutionTable
    template_name = None
    filter_class = InstitutionListFilter
    formhelper_class = InstitutionFilterFormHelper

    def render_to_response(self, context):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
        response = HttpResponse(content_type='application/xml; charset=utf-8')
        filename = "institutions_{}".format(timestamp)
        response['Content-Disposition'] = 'attachment; filename="{}.rdf"'.format(filename)
        g = inst_to_arche(self.get_queryset())
        get_format = self.request.GET.get('format', default='n3')
        result = g.serialize(destination=response, format=get_format)
        return response


class InstitutionDetailView(DetailView):
    model = Institution
    template_name = 'entities/institution_detail.html'

    def get_context_data(self, **kwargs):
        context = super(InstitutionDetailView, self).get_context_data(**kwargs)
        context['history'] = Version.objects.get_for_object(self.object)
        return context


class InstitutionCreate(BaseCreateView):

    model = Institution
    form_class = InstitutionForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(InstitutionCreate, self).dispatch(*args, **kwargs)


class InstitutionUpdate(BaseUpdateView):

    model = Institution
    form_class = InstitutionForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(InstitutionUpdate, self).dispatch(*args, **kwargs)


class InstitutionDelete(DeleteView):
    model = Institution
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('entities:browse_institutions')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(InstitutionDelete, self).dispatch(*args, **kwargs)


class PersonListView(GenericListView):
    model = Person
    table_class = PersonTable
    filter_class = PersonListFilter
    formhelper_class = PersonFilterFormHelper
    init_columns = [
        'id',
        'name',
    ]


class PersonRDFView(GenericListView):
    model = Person
    table_class = PersonTable
    template_name = None
    filter_class = PersonListFilter
    formhelper_class = PersonFilterFormHelper

    def render_to_response(self, context):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
        response = HttpResponse(content_type='application/xml; charset=utf-8')
        filename = "places_{}".format(timestamp)
        response['Content-Disposition'] = 'attachment; filename="{}.rdf"'.format(filename)
        g = person_to_arche(self.get_queryset())
        get_format = self.request.GET.get('format', default='n3')
        result = g.serialize(destination=response, format=get_format)
        return response


class PersonDetailView(DetailView):
    model = Person
    template_name = 'entities/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)
        context['history'] = Version.objects.get_for_object(self.object)
        return context


class PersonCreate(BaseCreateView):

    model = Person
    form_class = PersonForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PersonCreate, self).dispatch(*args, **kwargs)


class PersonUpdate(BaseUpdateView):

    model = Person
    form_class = PersonForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PersonUpdate, self).dispatch(*args, **kwargs)


class PersonDelete(DeleteView):
    model = Person
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('entities:browse_entities')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PersonDelete, self).dispatch(*args, **kwargs)


class AlternativeNameListView(GenericListView):
    model = AlternativeName
    table_class = AlternativeNameTable
    filter_class = AlternativeNameListFilter
    formhelper_class = AlternativeNameFilterFormHelper
    init_columns = [
        'id',
        'name',
    ]


class AlternativeNameDetailView(DetailView):
    model = AlternativeName
    template_name = 'entities/alternativenames_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AlternativeNameDetailView, self).get_context_data(**kwargs)
        context['history'] = Version.objects.get_for_object(self.object)
        return context


class AlternativeNameCreate(BaseCreateView):

    model = AlternativeName
    form_class = AlternativeNameForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AlternativeNameCreate, self).dispatch(*args, **kwargs)


class AlternativeNameUpdate(BaseUpdateView):

    model = AlternativeName
    form_class = AlternativeNameForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AlternativeNameUpdate, self).dispatch(*args, **kwargs)


class AlternativeNameDelete(DeleteView):
    model = AlternativeName
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('entities:browse_altnames')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AlternativeNameDelete, self).dispatch(*args, **kwargs)


class PlaceListView(GenericListView):
    model = Place
    table_class = PlaceTable
    filter_class = PlaceListFilter
    formhelper_class = PlaceFilterFormHelper
    init_columns = [
        'id',
        'name',
        'part_oc'
    ]


class PlaceRDFView(GenericListView):
    model = Place
    table_class = PlaceTable
    template_name = None
    filter_class = PlaceListFilter
    formhelper_class = PlaceFilterFormHelper

    def render_to_response(self, context):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
        response = HttpResponse(content_type='application/xml; charset=utf-8')
        filename = "places_{}".format(timestamp)
        response['Content-Disposition'] = 'attachment; filename="{}.rdf"'.format(filename)
        g = place_to_arche(self.get_queryset())
        get_format = self.request.GET.get('format', default='n3')
        result = g.serialize(destination=response, format=get_format)
        return response


class PlaceDetailView(DetailView):
    model = Place
    template_name = 'entities/place_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PlaceDetailView, self).get_context_data(**kwargs)
        context['history'] = Version.objects.get_for_object(self.object)
        return context


class PlaceCreate(BaseCreateView):

    model = Place
    form_class = PlaceForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PlaceCreate, self).dispatch(*args, **kwargs)


class PlaceUpdate(BaseUpdateView):

    model = Place
    form_class = PlaceForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PlaceUpdate, self).dispatch(*args, **kwargs)


class PlaceDelete(DeleteView):
    model = Place
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('entities:browse_places')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PlaceDelete, self).dispatch(*args, **kwargs)
