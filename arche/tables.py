import django_tables2 as tables
from django_tables2.utils import A
from .models import *


class ProjectTable(tables.Table):
    id = tables.LinkColumn(
        'arche:project_detail',
        args=[A('pk')], verbose_name='ID'
    )
    has_title = tables.LinkColumn(
        'arche:project_detail',
        args=[A('pk')], verbose_name=Project._meta.get_field('has_title').verbose_name
    )

    class Meta:
        model = Project
        sequence = ('id', 'has_title',)
        attrs = {"class": "table table-responsive table-hover"}


class CollectionTable(tables.Table):
    id = tables.LinkColumn(
        'arche:collection_detail',
        args=[A('pk')], verbose_name='ID'
    )
    has_title = tables.LinkColumn(
        'arche:collection_detail',
        args=[A('pk')], verbose_name=Collection._meta.get_field('has_title').verbose_name
    )

    class Meta:
        model = Collection
        sequence = ('id', 'has_title',)
        attrs = {"class": "table table-responsive table-hover"}


class ResourceTable(tables.Table):
    id = tables.LinkColumn(
        'arche:resource_detail',
        args=[A('pk')], verbose_name='ID'
    )
    has_title = tables.LinkColumn(
        'arche:resource_detail',
        args=[A('pk')], verbose_name=Project._meta.get_field('has_title').verbose_name
    )

    class Meta:
        model = Resource
        sequence = ('id', 'has_title',)
        attrs = {"class": "table table-responsive table-hover"}
