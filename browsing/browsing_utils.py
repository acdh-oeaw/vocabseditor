import datetime
import django_tables2
import time
import pandas as pd
import django_filters

from django.apps import apps
from django.conf import settings
from django.db.models.fields.related import ManyToManyField
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import BrowsConf
from guardian.shortcuts import get_objects_for_user
from guardian.mixins import PermissionRequiredMixin

if 'charts' in settings.INSTALLED_APPS:
    from charts.models import ChartConfig
    from charts.views import create_payload


def get_entities_table(model_class):
    class GenericEntitiesTable(django_tables2.Table):
        id = django_tables2.LinkColumn()

        class Meta:
            model = model_class
            attrs = {"class": "table table-hover table-striped table-condensed"}

    return GenericEntitiesTable


class GenericFilterFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(GenericFilterFormHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_class = 'genericFilterForm'
        self.form_method = 'GET'
        self.helper.form_tag = False
        self.add_input(Submit('Filter', 'Search'))


django_filters.filters.LOOKUP_TYPES = [
    ('', '---------'),
    ('exact', 'Is equal to'),
    ('iexact', 'Is equal to (case insensitive)'),
    ('not_exact', 'Is not equal to'),
    ('lt', 'Lesser than/before'),
    ('gt', 'Greater than/after'),
    ('gte', 'Greater than or equal to'),
    ('lte', 'Lesser than or equal to'),
    ('startswith', 'Starts with'),
    ('endswith', 'Ends with'),
    ('contains', 'Contains'),
    ('icontains', 'Contains (case insensitive)'),
    ('not_contains', 'Does not contain'),
]


class GenericListView(django_tables2.SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'
    paginate_by = 25
    template_name = 'browsing/generic_list.html'
    init_columns = []

    def get_table_class(self):
        if self.table_class:
            return self.table_class
        else:
            return get_entities_table(self.model)
        # TODO unreachable
        # raise ImproperlyConfigured(
        #     "You must either specify {0}.table_class or {0}.model".format(type(self).__name__)
        # )

    def get_all_cols(self):
        print('get_table')
        print(self.get_table().base_columns.keys())
        all_cols = list(self.get_table().base_columns.keys())
        return all_cols

    def get_queryset(self, **kwargs):
        qs = get_objects_for_user(self.request.user,
                                  perms=[
                                      'view_{}'.format(self.model.__name__.lower()),
                                      'change_{}'.format(self.model.__name__.lower()),
                                      'delete_{}'.format(self.model.__name__.lower()),
                                  ],
                                  klass=self.model)
        # qs = super(GenericListView, self).get_queryset()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(GenericListView, self).get_table()
        default_cols = self.init_columns
        all_cols = table.base_columns.keys()
        selected_cols = self.request.GET.getlist("columns") + default_cols
        exclude_vals = [x for x in all_cols if x not in selected_cols]
        table.exclude = exclude_vals
        return table

    def get_context_data(self, **kwargs):
        context = super(GenericListView, self).get_context_data()
        togglable_colums = [x for x in self.get_all_cols() if x not in self.init_columns]
        context['togglable_colums'] = togglable_colums
        context[self.context_filter_name] = self.filter
        context['docstring'] = "{}".format(self.model.__doc__)
        context['class_name'] = "{}".format(self.model._meta.verbose_name)
        try:
            context['get_arche_dump'] = self.model.get_arche_dump()
        except AttributeError:
            context['get_arche_dump'] = None
        try:
            context['create_view_link'] = self.model.get_createview_url()
        except AttributeError:
            context['create_view_link'] = None
        try:
            context['download'] = self.model.get_dl_url()
        except AttributeError:
            context['download'] = None
        model_name = self.model.__name__.lower()
        context['entity'] = model_name
        context['conf_items'] = list(
            BrowsConf.objects.filter(model_name=model_name)
                .values_list('field_path', 'label')
        )
        print(context['conf_items'])
        if 'charts' in settings.INSTALLED_APPS:
            context['vis_list'] = ChartConfig.objects.filter(model_name=model_name)
            context['property_name'] = self.request.GET.get('property')
            context['charttype'] = self.request.GET.get('charttype')
            if context['charttype'] and context['property_name']:
                qs = self.get_queryset()
                chartdata = create_payload(
                    context['entity'],
                    context['property_name'],
                    context['charttype'],
                    qs
                )
                context = dict(context, **chartdata)
        return context

    def render_to_response(self, context, **kwargs):
        download = self.request.GET.get('sep', None)
        if download:
            sep = self.request.GET.get('sep', ',')
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
            filename = "export_{}".format(timestamp)
            response = HttpResponse(content_type='text/csv')
            if context['conf_items']:
                conf_items = context['conf_items']
                try:
                    df = pd.DataFrame(
                        list(
                            self.get_queryset().values_list(*[x[0] for x in conf_items])
                        ),
                        columns=[x[1] for x in conf_items]
                    )
                except AssertionError:
                    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(
                        filename
                    )
                    return response
            else:
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            if sep == "comma":
                df.to_csv(response, sep=',', index=False)
            elif sep == "semicolon":
                df.to_csv(response, sep=';', index=False)
            elif sep == "tab":
                df.to_csv(response, sep='\t', index=False)
            else:
                df.to_csv(response, sep=',', index=False)
            response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
            return response
        else:
            response = super(GenericListView, self).render_to_response(context)
            return response


class BaseCreateView(CreateView):
    model = None
    form_class = None
    template_name = 'browsing/generic_create.html'

    def get_context_data(self, **kwargs):
        context = super(BaseCreateView, self).get_context_data()
        context['docstring'] = "{}".format(self.model.__doc__)
        context['class_name'] = "{}".format(self.model._meta.verbose_name)
        return context


class BaseUpdateView(PermissionRequiredMixin, UpdateView):
    model = None
    form_class = None
    template_name = 'browsing/generic_create.html'
    permission_required = None
    return_403 = True

    # or raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(BaseUpdateView, self).get_context_data()
        context['docstring'] = "{}".format(self.model.__doc__)
        context['class_name'] = "{}".format(self.model._meta.verbose_name)
        return context


def model_to_dict(instance):
    """
    serializes a model.object to dict, including non editable fields as well as
    ManyToManyField fields
    Taken from https://stackoverflow.com/questions/21925671/
    """
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                try:
                    data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
                except Exception as e:
                    print(e)
                    data[f.name] = []
        else:
            data[f.name] = f.value_from_object(instance)
    return data


def create_brows_config_obj(app_name, exclude_fields=[]):
    """
    Creates BrowsConf objects for all models defined in chosen app
    """
    exclude = exclude_fields
    try:
        models = [x for x in apps.get_app_config(app_name).get_models()]
    except LookupError:
        print("The app '{}' does not exist".format(app_name))
        return False

    for x in models:
        model_name = "{}".format(x.__name__.lower())
        print("Model: {}".format(model_name))
        for f in x._meta.get_fields(include_parents=False):
            if f.name not in exclude:
                field_name = f.name
                verbose_name = getattr(f, 'verbose_name', f.name)
                help_text = getattr(f, 'help_text', 'no helptext')
                print("{}: {} ({})".format(model_name, field_name, help_text))
                brc, _ = BrowsConf.objects.get_or_create(
                    model_name=model_name,
                    field_path=field_name,
                )
                brc.label = verbose_name
                brc.save()
            else:
                print("skipped: {}".format(f.name))
