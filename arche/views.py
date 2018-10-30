import time
import datetime
import rdflib
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django_tables2 import SingleTableView, RequestConfig
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from .models import Project, Collection, Resource
from .forms import *
from .filters import *
from .tables import *
from .serializer_arche import *
from browsing.browsing_utils import GenericListView, BaseCreateView, BaseUpdateView


def copy_view(request):
    """View looks for get-params with: name of application, of model and id\
    of instance of model which should be copied"""

    class_name = request.GET.get('class-name', '')
    object_id = request.GET.get('id', '')
    app_name = request.GET.get('app-name', 'arche')
    if object_id and class_name:
        class_name = class_name.lower()
        app_name = app_name.lower()
        try:
            object_id = int(object_id)
        except ValueError:
            html = "<html><body>Wrong format of id-param</body></html>"
            return HttpResponse(html)
        try:
            cont_type = ContentType.objects.get(app_label=app_name, model=class_name)
        except ObjectDoesNotExist:
            html = "<html><body>Wrong format of class_name-param</body></html>"
            return HttpResponse(html)
        try:
            current_object = cont_type.get_object_for_this_type(id=object_id)
        except ObjectDoesNotExist:
            html = "<html><body>Resource matching query does not exist.</body></html>"
            return HttpResponse(html)
        new_object = current_object.copy_instance()
        try:
            return redirect(new_object)
        except:
            html = """<html>
            <body>The object was saved but somehting is wrong with the redirect.
            Please check if the Class of the instance you try to copy has a
            get_absolute_url method defined</body>
            </html>"""
            return HttpResponse(html)
    else:
        html = """<html>
        <body>Either id or class-name params are missing</body>
        </html>"""
        return HttpResponse(html)


class ProjectListView(GenericListView):
    model = Project
    table_class = ProjectTable
    filter_class = ProjectListFilter
    formhelper_class = ProjectFilterFormHelper
    init_columns = [[
        'id',
        'has_title',
    ]]


class ProjectRDFView(GenericListView):
    model = Project
    table_class = ProjectTable
    template_name = None
    filter_class = ProjectListFilter
    formhelper_class = ProjectFilterFormHelper

    def render_to_response(self, context):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
        response = HttpResponse(content_type='application/xml; charset=utf-8')
        filename = "{}_{}".format(self.model.__name__, timestamp)
        response['Content-Disposition'] = 'attachment; filename="{}.rdf"'.format(filename)
        g = project_to_arche(self.get_queryset())
        get_format = self.request.GET.get('format', default='n3')
        result = g.serialize(destination=response, format=get_format)
        return response


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'arche/project_detail.html'


class ProjectCreate(BaseCreateView):

    model = Project
    form_class = ProjectForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreate, self).dispatch(*args, **kwargs)


class ProjectUpdate(BaseUpdateView):

    model = Project
    form_class = ProjectForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdate, self).dispatch(*args, **kwargs)


class ProjectDelete(DeleteView):
    model = Project
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('arche:browse_projects')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectDelete, self).dispatch(*args, **kwargs)


class CollectionListView(GenericListView):
    model = Collection
    table_class = CollectionTable
    filter_class = CollectionListFilter
    formhelper_class = CollectionFilterFormHelper
    init_columns = [
        'id',
        'has_title'
    ]


class CollectionRDFView(GenericListView):
    model = Collection
    table_class = CollectionTable
    template_name = None
    filter_class = CollectionListFilter
    formhelper_class = CollectionFilterFormHelper

    def render_to_response(self, context):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
        response = HttpResponse(content_type='application/xml; charset=utf-8')
        filename = "{}_{}".format(self.model.__name__, timestamp)
        response['Content-Disposition'] = 'attachment; filename="{}.rdf"'.format(filename)
        g = collection_to_arche(self.get_queryset())
        get_format = self.request.GET.get('format', default='n3')
        result = g.serialize(destination=response, format=get_format)
        return response


class CollectionDetailView(DetailView):
    model = Collection
    template_name = 'arche/collection_detail.html'


class CollectionCreate(BaseCreateView):

    model = Collection
    form_class = CollectionForm
    # template_name = 'arche/collection_create.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CollectionCreate, self).dispatch(*args, **kwargs)


class CollectionUpdate(BaseUpdateView):

    model = Collection
    form_class = CollectionForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CollectionUpdate, self).dispatch(*args, **kwargs)


class CollectionDelete(DeleteView):
    model = Collection
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('arche:browse_collections')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CollectionDelete, self).dispatch(*args, **kwargs)


class ResourceListView(GenericListView):
    model = Resource
    table_class = ResourceTable
    filter_class = ResourceListFilter
    formhelper_class = ResourceFilterFormHelper
    init_columns = [
        'id',
        'has_title',
    ]


class ResourceDetailView(DetailView):
    model = Resource
    template_name = 'arche/resource_detail.html'


class ResourceCreate(BaseCreateView):

    model = Resource
    form_class = ResourceForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ResourceCreate, self).dispatch(*args, **kwargs)


class ResourceUpdate(BaseUpdateView):

    model = Resource
    form_class = ResourceForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ResourceUpdate, self).dispatch(*args, **kwargs)


class ResourceDelete(DeleteView):
    model = Resource
    template_name = 'webpage/confirm_delete.html'
    success_url = reverse_lazy('arche:browse_resources')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ResourceDelete, self).dispatch(*args, **kwargs)


class ResourceInheritProperties(ResourceListView):
    template_name = 'arche/resource_browse.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ResourceInheritProperties, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ResourceInheritProperties, self).get_context_data()
        context[self.context_filter_name] = self.filter
        togglable_colums = [x for x in self.get_all_cols() if x not in self.init_columns]
        context['togglable_colums'] = togglable_colums
        new_props = []
        for x in self.get_queryset():
            new = x.inherit_properties()
        new_props.append(new)
        context['updat_report'] = new_props
        return context


class ResourceRDFView(GenericListView):
    model = Resource
    table_class = ResourceTable
    template_name = None
    filter_class = ResourceListFilter
    formhelper_class = ResourceFilterFormHelper

    def render_to_response(self, context):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
        response = HttpResponse(content_type='application/xml; charset=utf-8')
        filename = "{}_{}".format(self.model.__name__, timestamp)
        response['Content-Disposition'] = 'attachment; filename="{}.rdf"'.format(filename)
        g = resource_to_arche(self.get_queryset())
        get_format = self.request.GET.get('format', default='n3')
        result = g.serialize(destination=response, format=get_format)
        return response
